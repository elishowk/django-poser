# Django POSER

Work in progress

This Django app is essentially a REST API (tastypie)
It aims at managing and publishing pages hooked to third-party django apps (your app).
It was built as a publishing server of third-party/embedded web pages and JSON API.
It's historically a fork of Django-CMS without MPTT, nor Reversion, nor sekizai, nor placeholders, nor plugins, nor moderations, nor menus, nor the advanced django-admin GUI.

## Documentation

### Startup

Configure your django project including django-poser application.
Initialize a test database with 

  ~/your-project/ $ env/bin/python /path/to/django-poser/clone/runtestserver.py

Go to http://127.0.0.1:9000/test/

# A Poser's definition

  * <http://www.urbandictionary.com/define.php?term=poser>

> A person who attempts to blend into a specific social group : "Justin was such a poser-goth; sure, he comes to school in all black, but he doesn't even know who Edgar Allen Poe is."

### REST API

The rest API is built with [Django-Tastypie](http://tastypie.org) and provides 3 resources :

    {
      page: {
        list_endpoint: "/poser/poser_api/page/",
        schema: "/poser/poser_api/page/schema/"
      },
      site: {
        list_endpoint: "/poser/poser_api/site/",
        schema: "/poser/poser_api/site/schema/"
      },
      user: {
        list_endpoint: "/poser/poser_api/user/",
        schema: "/poser/poser_api/user/schema/"
      }
    }

A Page is the main model provided by this application

#### Page's config

  * GET config : http://127.0.0.1:9000/poser/test/

    {
        api_url: "127.0.0.1:9000/poser/poser_api/",
        page_id: 1,
        static_url: "/static/",
        host: "http://127.0.0.1:9000/",
        has_view_permissions: true,
        path: "http://127.0.0.1:9000/poser/test/",
        has_change_permissions: true
    }

Get this from any client to configure all the rest !

  * General config is also available on root URL http://127.0.0.1:9000/poser/
      {
          path: "http://127.0.0.1:9000/poser/",
          host: "http://127.0.0.1:9000/",
          page_id: "None",
          api_url: "127.0.0.1:9000/poser/poser_api/",
          static_url: "/static/"
      }

### Retrieve page list

  * Get the list of all widgets

#### Request

    $.ajax({
       url: "http://127.0.0.1:9000/poser/poser_api/page/",
       type: "GET",
       contentType: 'application/json'
    });

#### URL Parameters

  * {{id}} : optional model's ID the model

#### Data Parameters

 None

#### Returned values

Depending on the Apphook name written into the fiels "application", the API will replace the value with the associated app's model.

#### Server response: 200 OK

    {
      meta: {
      limit: 1000,
      next: null,
      offset: 0,
      previous: null,
      total_count: 1
    },
    objects: [
      {
        application: {
          icon: "",
          id: 1,
          img: "",
          moderators: [
          "/poser/poser_api/user/1/"
          ],
          page: "/poser/poser_api/page/1/",
          resource_uri: "/videotag/videotag_api/videotag/1/",
          speakers: [
          "/poser/poser_api/user/1/"
          ],
          state: 1,
          video: "http://www.youtube.com/watch?v=frlsGUHYu04",
          videotype: "youtube"
        },
        changed_by: "/poser/poser_api/user/0/",
        changed_date: "2012-12-20T14:39:53.672072",
        created_by: "/poser/poser_api/user/0/",
        creation_date: "2012-12-20T14:16:34.609972",
        id: 1,
        meta_description: "",
        meta_keywords: "",
        path: "test",
        publication_date: "2012-12-20T14:16:34",
        publication_end_date: null,
        published: true,
        redirect: "",
        resource_uri: "/poser/poser_api/page/1/",
        site: "/poser/poser_api/site/2/",
        slug: "test",
        title: "test"
      }
    ]}
  
#### Server response: 400 Bad Request


### Create a new page

* this ResourceModel class has been overwritten, please see : https://github.com/elishowk/django-poser/blob/master/poser/rest.py

#### Request
    
    $.ajax({
       url: "http://127.0.0.1:9000/poser/poser_api/page/",
       type: "POST",
       data: {
           created_by: {{user_username}},
           published: "true",
           title: "Bob Marley: Live in Santa Barbara ",    
           apphook: "Videotag";    
       },
       contentType: 'application/json'
    });

#### URL Parameters

 None
 
#### Data Parameters

  * IMPORTANT: The server require contentType: 'application/json'.
  * The example presented an exhaustive list of require fields to create a page. Of course the {{user_username}} is the logged one.

#### Returned values

#### Server response: 200 OK

The server will return the new page with all completed fields.


     "Object": {
         "Other": "data",
         "attributes": {
             "id": 4,
             "resource_uri": "/poser_api/v1/page/1"
             "user": "2", 
             "created_by": "/videotag_api/v1/user/2",
             "template_choices": "",
             "creation_date": "" 
             "changed_date": ""
             "publication_date": ""
             "publication_end_date": "",
             "published": "",
             "template": "",
             "site": "",    
             "title": "",    
             "slug": "",    
             "path": "",    
             "reverse_id": "",    
             "has_url_overwrite": "",    
             "redirect": "",    
             "meta_description": "",    
             "meta_keywords": "",    
             "login_required": "",    
             "objects": ""  
         },
         "Other": "data"
     }

#### Server response: 401 Unauthorized 

  * user is not logged in or hasn't the right permission
 
#### Server response: 400 Bad Request 

    "Object": { "error": "Invalid data parameters" } 
 
 
## User resource - The django user.

On this ressource, the basics informations of users are recorded.

### User's API

The basic information about Django's User model

#### Request

    $.ajax({
       url: "http://127.0.0.1:9000/poser/poser_api/user/1/",
       type: "GET"
    });
    
#### URL Parameters

    {{username}} : The client username 
 
#### Data Parameters

None
 
#### Returned values
#### Server response: 200 OK 

    {
      date_joined: "2012-12-20T14:21:31.763401",
      email: "",
      first_name: "",
      id: 1,
      last_login: "2012-12-20T14:21:31.763389",
      last_name: "",
      resource_uri: "/poser/poser_api/user/1/",
      username: "testuser"
    }
 
#### Server response: 401 Unauthorized

### Modify user's informations

An user can modify his own data 

#### Request

    $.ajax({
       url: "http://127.0.0.1:9000/poser/poser_api/user/{{id}}/",
       type: "PUT",
       data: {
           email: 'Zion@gmail.com'
           first_name : 'Robert'
           last_name : 'Marley'
           username : 'Bob Marley'           
       },
       contentType: 'application/json'
    });

#### URL Parameters
 
    {{id}} Required user id

#### Data Parameters

IMPORTANT: The server require contentType: 'application/json'.
The example presented an exhaustive list of possible fields to modify. Of course none of them are required.


#### Returned values
#### Serveur response: 200 OK

The server will return the new state of the modified user.   
 

#### Serveur response: 401 Unauthorized 

    "Object": { "error": "{{id}} is not the authenticated user " }

#### Serveur response: 400 Bad Request 

    "Object": { "error": "Invalid data parameters" } 

## Credits

* Maintainer : me <elias point showk at commonecoute point fr> @ CommOnEcoute SAS, Paris, France
* This is a fork of [django-cms](https://github.com/divio/django-cms)

## License

* GNU Affero General Public Licence v3
