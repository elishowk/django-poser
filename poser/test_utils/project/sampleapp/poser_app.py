from poser.app_base import POSERApp
from poser.apphook_pool import apphook_pool


class SampleApp(POSERApp):
    name = "SampleApp"
    module = 'poser.test_utils.project.sampleapp.models'
    klass = 'PictureResource'
    urls = ["poser.test_utils.project.sampleapp.urls"]


apphook_pool.register(SampleApp)
