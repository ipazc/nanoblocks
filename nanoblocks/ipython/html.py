import pkg_resources

HTML = {
    'account': 'ipython/html/account.html',
    'block_send': 'ipython/html/block_send.html',
    'block_receive': 'ipython/html/block_receive.html',
    'block_change': 'ipython/html/block_change.html',
}


def get_html(html_name):
    return str(pkg_resources.resource_stream('nanoblocks', HTML[html_name]).read(), "utf-8")
