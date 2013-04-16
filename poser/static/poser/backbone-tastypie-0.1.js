/**
 * Backbone-tastypie.js 0.1
 * join worked by (c) 2011 Paul Uithol
 * and https://github.com/amccloud/backbone-tastypie
 *
 * Backbone-tastypie may be freely distributed under the MIT license.
 * Add Backbone.js functionality, for compatibility with django-tastypie.
 */

define(['backbone'],
       function(Backbone) {
           Backbone.Tastypie = {
               defaultLimit: 20,
               getAfterEmptyPost: false,
               getAfterEmptyPut: false,
               apiKey: {
                   username: '',
                   key: ''
               },
               csrfToken: ''
           };
           /*
            * Global AJAX setup
            */
           Backbone.$.ajaxSetup({
               beforeSend: function(jqXHR, settings) {
                   // TODO CSRF, Auth, User, etc...
               }
           });

           function tastypieSync(method, model, options) {
               var headers = '';

               if (Backbone.Tastypie.apiKey &&
                   Backbone.Tastypie.apiKey.username.length) {
                   headers = _.extend({
                       'Authorization': 'ApiKey ' +
                           Backbone.Tastypie.apiKey.username +
                           ':' +
                           Backbone.Tastypie.apiKey.key
                   }, options.headers);
                   options.headers = headers;
               }

               if (Backbone.Tastypie.csrfToken &&
                   Backbone.Tastypie.csrfToken.length) {
                   headers = _.extend({
                       'X-CSRFToken': Backbone.Tastypie.csrfToken
                   }, options.headers);
                   options.headers = headers;
               }

               if ((method === 'create' &&
                    Backbone.Tastypie.getAfterEmptyPost) ||
                   (method === 'update' &&
                    Backbone.Tastypie.getAfterEmptyPut)) {
                    var dfd = new $.Deferred();
                    // Set up 'success' handling
                    dfd.done(options.success);
                    options.success = function(resp, status, xhr) {
                        if (!resp || resp == '' || xhr.status === 204) {
                            var location = xhr.getResponseHeader('Location') ||
                                model.id;
                            return $.ajax({
                                url: location,
                                headers: headers,
                                success: dfd.resolve,
                                error: dfd.reject
                            });
                        }
                        else {
                            return dfd.resolveWith(options.context || options,
                                                   [resp, status, xhr]);
                        }
                    };

                    // Set up 'error' handling
                    dfd.fail(options.error);
                    options.error = function(xhr, status, resp) {
                        dfd.rejectWith(options.context || options,
                                       [xhr, status, resp]);
                    };

                    // Make the request, make it accessibly by assigning
                    // it to the 'request' property on the deferred
                    dfd.request = Backbone.sync(method, model, options);
                    return dfd;
               }

               return Backbone.sync(method, model, options);
           };
           function addSlash(str) {
               return str +
                   ((str.length > 0 &&
                     str.charAt(str.length - 1) === '/') ? '' : '/');
           };

           Backbone.Tastypie.Model = Backbone.Model.extend({
               idAttribute: 'resource_uri',
               sync: tastypieSync,
               url: function() {
                   var url = (_.isFunction(this.urlRoot) ?
                              this.urlRoot() : this.urlRoot);
                   url = url || this.collection &&
                       (_.isFunction(this.collection.url) ?
                        this.collection.url() : this.collection.url);
                   if (url && this.has('id')) {
                       url = addSlash(url) + this.get('id');
                   }
                   return url || urlError();
               },
               _getId: function() {
                   if (this.has('id'))
                       return this.get('id');

                   return _.chain(
                       this.get('resource_uri').split('/'))
                       .compact().last().value();
               },
               parse: function(data) {
                   return data && data.objects &&
                       (_.isArray(data.objects) ?
                        data.objects[0] : data.objects) || data;
               }
           });

           Backbone.Tastypie.Collection = Backbone.Collection.extend({
                constructor: function(models, options) {
                    this.meta = {};
                    this.filters = {};

                    Backbone.Collection.prototype.constructor.apply(
                        this, arguments);

                    _.defaults(this.filters, {
                        limit: Backbone.Tastypie.defaultLimit,
                        offset: 0
                    });

                    if (options && options.filters)
                        _.extend(this.filters, options.filters);
                },
                sync: tastypieSync,
                /*
                * Allow for urlRoot function or string
                */
                url: function() {
                    var url = (_.isFunction(this.urlRoot) ?
                              this.urlRoot() : this.urlRoot);
                    return url + this._getQueryString();
                },
                /*
                 * Resets urlRoot depending on
                 * whether you give a list of model ids
                 */
                setUrlRoot: function(models) {
                    var url = this.urlRoot;
                    if (_.isArray(models) && models.length > 0) {
                        var decompose = url.split('?');
                        if (decompose[0].match(/\/set\//gi)) {
                            decompose[0] = decompose[0].replace(
                                    /\/set\/(\w)(;\w)*\//gi,
                                    '/set/' + models.join(';') + '/');
                        } else {
                            decompose[0] += 'set/' + models.join(';') + '/';
                        }
                        url = decompose[0];
                    }
                    this.urlRoot = url;
                },
                /**
                    * Change urlRoot using an array of URIs instead of IDs
                    *
                    * @param {Array} uris array of URIs
                    * @return {Backbone.Collection}
                    *
                    * @api public
                    */
                setIds: function(uris) {
                    if (! _.isArray(uris) || uris.length < 1) {
                        return this;
                    }

                    this.setUrlRoot(uris.map(function(uri) {
                        return (uri.match(/(\d+)\/?$/) || [])[1];
                    }));

                    return this;
                },
                getById: function(id) {
                    for (var i = 0; i < this.models.length; i++)
                            if (this.models[i].get('id') === parseInt(id))
                                return this.models[i];
                },
                parse: function(response) {
                    if (response && response.meta)
                        this.meta = response.meta;
                    return response && response.objects;
                },
                fetchNext: function(options) {
                    options = options || {};
                    options.add = true;

                    this.filters.limit = this.meta.limit;
                    this.filters.offset = this.meta.offset + this.meta.limit;

                    if (this.filters.offset > this.meta.total_count)
                        this.filters.offset = this.meta.total_count;

                    return this.fetch.call(this, options);
                },
                fetchPrevious: function(options) {
                    options = options || {};
                    options.add = true;
                    options.at = 0;

                    this.filters.limit = this.meta.limit;
                    this.filters.offset = this.meta.offset - this.meta.limit;

                    if (this.filters.offset < 0) {
                        this.filters.limit += this.filters.offset;
                        this.filters.offset = 0;
                    }

                    return this.fetch.call(this, options);
                },
                _getQueryString: function() {
                    if (!this.filters)
                        return '';

                    return '?' + $.param(this.filters);
                }
            });

            // Helper function from Backbone to get a value from a Backbone
            // object as a property or as a function.
            var getValue = function(object, prop) {
                if ((object && object[prop]))
                    return _.isFunction(object[prop]) ?
                        object[prop]() : object[prop];
            };

            // Helper function from Backbone that raises error when a model's
            // url cannot be determined.
            var urlError = function() {
                throw new Error('"url" property or function must be specified');
            };
            return Backbone;
        });
