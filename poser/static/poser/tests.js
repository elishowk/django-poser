/**
 * Tests.
 */
require([
    'lib/chai-1.4.0'
    ], function(chai) {

        var url = 'http://127.0.0.1:9000/poser/poser_api/';
        var page_title = Date.now() + '';
        describe('testing poser REST API at ' + url, function() {

            it('get all pages', function(done) {
                $.ajax({
                    url: url + 'page/',
                    success: function(data) {
                        console.log(data);
                        done();
                    },
                    type: 'GET',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });
            it('insert one page', function(done) {
                $.ajax({
                    url: url + 'page/',
                    data: JSON.stringify({
                        application: 'SampleApp',
                        title: page_title,
                        published: true
                    }),
                    success: function(data) {
                        expect(data.id).to.be.a('number');
                        expect(data.slug).to.be.a('string');
                        expect(data.application).to.equal('SampleApp');
                        expect(data.published).to.equal(true);
                        expect(data.title).to.equal(page_title);
                        done();
                    },
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });
            it('check if page is published', function(done) {
                this.timeout(4000);
                $.ajax({
                    url: url + 'page/',
                    data: JSON.stringify({
                        title: page_title,
                        published: true
                    }),
                    success: function(data) {
                        expect(data.id).to.be.a('number');
                        expect(data.slug).to.be.a('string');
                        //expect(data.application).to.equal();
                        expect(data.published).to.equal(true);
                        expect(data.title).to.equal(page_title);
                        $.ajax({
                            url: 'http://127.0.0.1:9000/poser/' + data.path,
                            success: function() {
                                done();
                            }
                        });
                    },
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });
            it('insert and delete one page', function(done) {
                this.timeout(4000);
                $.ajax({
                    url: url + 'page/',
                    data: JSON.stringify({
                        title: page_title,
                        published: true
                    }),
                    success: function(data) {
                        expect(data.id).to.be.a('number');
                        expect(data.slug).to.be.a('string');
                        //expect(data.application).to.equal();
                        expect(data.published).to.equal(true);
                        expect(data.title).to.equal(page_title);
                        var path = data.path;
                        $.ajax({
                            url: url + 'page/' + data.id,
                            success: function(data) {
                                $.ajax({
                                    url: 'http://127.0.0.1:9000/poser/' + path,
                                    error: function() {
                                        done();
                                    }
                                });
                            },
                            type: 'DELETE',
                            contentType: 'application/json',
                            dataType: 'json'
                        });
                    },
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });
            it('insert and modify one page', function(done) {
                this.timeout(4000);
                $.ajax({
                    url: url + 'page/',
                    data: JSON.stringify({
                        title: page_title,
                        published: true
                    }),
                    success: function(data) {
                        expect(data.id).to.be.a('number');
                        expect(data.slug).to.be.a('string');
                        //expect(data.application).to.equal();
                        expect(data.published).to.equal(true);
                        expect(data.title).to.equal(page_title);

                        $.ajax({
                            url: url + 'page/' + data.id,
                            success: function(data) {
                                expect(data.published).to.equal(false);
                                expect(data.title).to.equal(page_title + "testmodify");
                                done();
                            },
                            data: JSON.stringify({
                                title: page_title + "testmodify",
                                published: false
                            }),
                            type: 'PUT',
                            contentType: 'application/json',
                            dataType: 'json'
                        });
                    },
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });
            it('unpublish page', function(done) {
                this.timeout(4000);
                $.ajax({
                    url: url + 'page/',
                    data: JSON.stringify({
                        title: page_title,
                        published: true
                    }),
                    success: function(data) {
                        $.ajax({
                            url: url + 'page/' + data.id,
                            success: function(data) {
                                expect(data.published).to.equal(false);
                                $.ajax({
                                    url: 'http://127.0.0.1:9000/poser/' + data.path,
                                    error: function() {
                                        done();
                                    }
                                });
                            },
                            data: JSON.stringify({
                                published: false
                            }),
                            type: 'PUT',
                            contentType: 'application/json',
                            dataType: 'json'
                        });
                    },
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json'
                });
            });

        });

        expect = chai.expect;
        if (window.mochaPhantomJS) { mochaPhantomJS.run(); }
        else { mocha.run(); }

});
