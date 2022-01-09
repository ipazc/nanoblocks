from nanoblocks import rcParams
from nanoblocks.block.block import Block
from nanoblocks.ipython.html import get_html
from nanoblocks.ipython.img import get_svg


class BlockChange(Block):
    """
    Represents a representative change block.
    Gives an easy interface for change blocks.
    """
    @property
    def representative(self):
        """
        Retrieves the new representative, the one changed to by this block.
        """
        return self.accounts.lazy_fetch(self._block_definition['representative'])

    def __str__(self):
        string = super().__str__()
        string += f"\tNew representative: {self.representative.address}\n\tLocal date: {self.local_timestamp}\n"
        return string

    def _repr_html_(self):
        template_html = get_html("block_change")
        date_format = rcParams["display.date_format"]

        formatted_template = template_html.format(**{
            "account_address": self.account_owner.address,
            "block_type": self.subtype,
            "block_hash": self.hash,
            "block_type_img": get_svg("block_receive"),
            "block_num": self.height,
            "copy_to_clipboard_image": get_svg("clipboard"),
            "block_type_str": self.subtype,
            "new_representative_address": self.representative.address,
            "transaction_date": self.local_timestamp.strftime(date_format),
            "confirmed_img": get_svg('confirmed') if self.confirmed else ""
        })

        return formatted_template
