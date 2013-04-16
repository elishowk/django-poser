require.config({
    'paths': {
        'backbone': 'lib/backbone-0.9.9.min',
        'jquery':   'lib/jquery-1.8.3.min',
        'underscore': 'lib/lodash-1.0.0.min',
        'modules':  'videotag-widget/modules',
    },
    'shim': {
        'backbone': {
            'deps': [
                'underscore',
                'jquery'
            ],
            'exports': 'Backbone'
        }
    }
});


require.appConfig = {
    'baseUrl': '/static/',
    'poserApiUrl': '/poser/poser_api/'
};
