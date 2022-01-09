import pkg_resources

IMAGES = {
    'clipboard': 'ipython/img/clipboard-svgrepo-com.svg',
    'block_receive': 'ipython/img/inbox-svgrepo-com.svg',
    'block_send': 'ipython/img/outbox-svgrepo-com.svg',
    'total_balance': 'ipython/img/dry-svgrepo-com.svg',
    'confirmed_balance': 'ipython/img/confirmed-svgrepo-com.svg',
    'pending_balance': 'ipython/img/shifts-pending-svgrepo-com.svg',
    'confirmed': 'ipython/img/ok-svgrepo-com.svg',
}


def get_svg(img_name):
    return str(pkg_resources.resource_stream('nanoblocks', IMAGES[img_name]).read(), "utf-8")
