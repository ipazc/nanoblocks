from nanoblocks import rcParams
from nanoblocks.block.block import Block
from nanoblocks.currency import Amount
from nanoblocks.ipython.html import get_html
from nanoblocks.ipython.img import get_svg


class BlockReceive(Block):
    """
    Represents a receive block.

    Gives an easy interface for receive blocks.
    """
    @property
    def source_account(self):
        """
        Retrieves the account source of the amount.
        It is the account that sent the amount of this block.
        """
        return self.accounts.lazy_fetch(self._block_definition['account'])

    @property
    def amount(self):
        """
        Retrieves the amount of Nano received.
        """
        return Amount(self._block_definition['amount'], unit="raw")

    def __str__(self):
        string = super().__str__()
        string += f"\tSource account: {self.source_account.address}\n\tAmount: {self.amount.as_unit(rcParams['currency.unit']).format()}\n\tLocal date: {self.local_timestamp}\n"
        return string

    def _repr_html_(self):
        template_html = get_html("block_receive")
        date_format = rcParams["display.date_format"]

        formatted_template = template_html.format(**{
            "account_address": self.account_owner.address,
            "block_type": self.subtype,
            "block_hash": self.hash,
            "block_type_img": get_svg("block_receive"),
            "block_num": self.height,
            "copy_to_clipboard_image": get_svg("clipboard"),
            "source_account": self.source_account.address,
            "block_type_str": self.subtype,
            "amount_str": str(self.amount.as_unit("NANO")),
            "amount": self.amount.as_unit("NANO").format(),
            "total_balance_image": get_svg("total_balance"),
            "transaction_date": self.local_timestamp.strftime(date_format),
            "confirmed_img": get_svg('confirmed') if self.confirmed else ""
        })

        return formatted_template
