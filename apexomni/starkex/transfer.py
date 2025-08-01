from collections import namedtuple
import math

from apexomni.constants import COLLATERAL_ASSET, ASSET_RESOLUTION
from apexomni.starkex.constants import ONE_HOUR_IN_SECONDS, ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
from apexomni.starkex.constants import TRANSFER_FIELD_BIT_LENGTHS
from apexomni.starkex.constants import TRANSFER_PADDING_BITS
from apexomni.starkex.constants import TRANSFER_PREFIX
from apexomni.starkex.constants import TRANSFER_FEE_ASSET_ID
from apexomni.starkex.constants import TRANSFER_MAX_AMOUNT_FEE
from apexomni.starkex.helpers import nonce_from_client_id
from apexomni.starkex.helpers import to_quantums_exact
from apexomni.starkex.signable import Signable
from apexomni.starkex.starkex_resources.proxy import get_hash

StarkwareTransfer = namedtuple(
    'StarkwareTransfer',
    [
        'sender_position_id',
        'receiver_position_id',
        'receiver_public_key',
        'quantums_amount',
        'nounce',
        'expiration_epoch_hours',
    ],
)


class SignableTransfer(Signable):
    """
    Wrapper object to convert a transfer, and hash, sign, and verify its
    signature.
    """

    def __init__(
        self,
        sender_position_id,
        receiver_position_id,
        receiver_public_key,
        human_amount,
        client_id,
        expiration_epoch_seconds,
        network_id,
        collateral_id,
    ):
        nounce = nonce_from_client_id(client_id)

        self.collateral_asset_id = int(
            collateral_id,
            16,
        )
        # The transfer asset is always the collateral asset.
        quantums_amount = to_quantums_exact(
            human_amount,
            ASSET_RESOLUTION[COLLATERAL_ASSET],
        )

        # Convert to a Unix timestamp (in hours).
        expiration_epoch_hours = math.ceil(
            float(expiration_epoch_seconds) / ONE_HOUR_IN_SECONDS,
        ) + ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS

        receiver_public_key = (
            receiver_public_key
            if isinstance(receiver_public_key, int)
            else int(receiver_public_key, 16)
        )

        message = StarkwareTransfer(
            sender_position_id=int(sender_position_id),
            receiver_position_id=int(receiver_position_id),
            receiver_public_key=receiver_public_key,
            quantums_amount=quantums_amount,
            nounce=nounce,
            expiration_epoch_hours=expiration_epoch_hours
        )

        super(SignableTransfer, self).__init__(message)

    def to_starkware(self):
        return self._message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware order."""
        # TODO: Check values are in bounds

        asset_ids = get_hash(
            self.collateral_asset_id,
            TRANSFER_FEE_ASSET_ID,
        )

        part1 = get_hash(
            asset_ids,
            self._message.receiver_public_key,
        )

        part2 = self._message.sender_position_id
        part2 <<= TRANSFER_FIELD_BIT_LENGTHS['position_id']
        part2 += self._message.receiver_position_id
        part2 <<= TRANSFER_FIELD_BIT_LENGTHS['position_id']
        part2 += self._message.sender_position_id
        part2 <<= TRANSFER_FIELD_BIT_LENGTHS['nonce']
        part2 += self._message.nounce

        part3 = TRANSFER_PREFIX
        part3 <<= TRANSFER_FIELD_BIT_LENGTHS['quantums_amount']
        part3 += self._message.quantums_amount
        part3 <<= TRANSFER_FIELD_BIT_LENGTHS['quantums_amount']
        part3 += TRANSFER_MAX_AMOUNT_FEE
        part3 <<= TRANSFER_FIELD_BIT_LENGTHS['expiration_epoch_hours']
        part3 += self._message.expiration_epoch_hours
        part3 <<= TRANSFER_PADDING_BITS

        return get_hash(
            get_hash(
                part1,
                part2,
            ),
            part3,
        )
