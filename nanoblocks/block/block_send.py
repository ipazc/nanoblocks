from nanoblocks import rcParams
from nanoblocks.block.block import Block
from nanoblocks.currency import Amount
from nanoblocks.ipython.html import get_html
from nanoblocks.ipython.img import get_svg


class BlockSend(Block):
    """
    Represents a send block.

    Gives an easy interface for send blocks.
    """

    @property
    def destination_account(self):
        """
        Retrieves the account target for the amount.
        It is the account where this amount is sent to.
        """
        account_address = self._block_definition.get('link_as_account') or self._block_definition.get('account', None)
        account = self.accounts.lazy_fetch(account_address)

        return account

    @property
    def amount(self):
        """
        Retrieves the amount of Nano received in case the block is read from the ledger.
        """
        result = Amount(self._block_definition['amount'], unit="raw")

        return result

    def __str__(self):
        string = super().__str__()
        string += f"\tDestination account: {self.destination_account.address if self.destination_account else 'Unknown (check block directly by hash)'}\n\tAmount: {self.amount.as_unit(rcParams['currency.unit']).format()}\n\tLocal date: {self.local_timestamp}\n"
        return string

    def _repr_html_(self):
        template_html = get_html("block_send")
        date_format = rcParams["display.date_format"]

        formatted_template = template_html.format(**{
            "account_address": self.account_owner.address,
            "block_type": self.subtype,
            "block_hash": self.hash,
            "block_type_img": get_svg("block_send"),
            "block_num": self.height,
            "copy_to_clipboard_image": get_svg("clipboard"),
            "destination_account": self.destination_account.address,
            "block_type_str": self.subtype,
            "amount_str": str(self.amount.as_unit("NANO")),
            "amount": self.amount.as_unit("NANO").format(),
            "total_balance_image": get_svg("total_balance"),
            "transaction_date": self.local_timestamp.strftime(date_format),
            "confirmed_img": get_svg('confirmed') if self.confirmed else ""
        })

        return formatted_template
