import productmd
import urllib

class ComposeInfo():
    def __init__(self, location, location_http):
        self.location = location
        self.metadata = productmd.compose.Compose(location_http)
        self._treeinfos = {}

    def tree_url(self, variant, architecture):
        for variant_metadata in self.metadata.info.get_variants():
            if variant_metadata.id == variant:
                return '/'.join([self.location, variant_metadata.paths.os_tree[architecture]])
        raise Exception(f'No variant "{variant}" was found in compose stored at: {self.location}')

    def treeinfo(self, variant, architecture):
        if (variant, architecture) not in self._treeinfos:
            url = '/'.join([self.tree_url(variant, architecture), '.treeinfo'])
            if url.startswith('/'):
                url = f'file://{url}'
            ti = productmd.treeinfo.TreeInfo()
            ti.loads(urllib.request.urlopen(url).read().decode())
            self._treeinfos[(variant, architecture)] = ti
        return self._treeinfos[(variant, architecture)]

    def kernel_path(self, variant, architecture):
        return self.treeinfo(variant, architecture).images[architecture]['kernel']

    def initrd_path(self, variant, architecture):
        return self.treeinfo(variant, architecture).images[architecture]['initrd']
