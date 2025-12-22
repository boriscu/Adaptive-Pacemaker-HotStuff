from typing import Dict, Optional
import collections
from hotstuff.domain.models import VoteMsg, QC, QCSignature, PartialSignature
from hotstuff.config import config
from hotstuff.logger import logger

class VoteAggregator:
    """
    Manages vote collection and QC formation.
    """
    def __init__(self, my_id: int):
        self.my_id = my_id
        # Vote Collection: view -> block_hash -> Set[replica_id] -> PartialSignature
        self.votes: Dict[int, Dict[str, Dict[int, PartialSignature]]] = collections.defaultdict(
            lambda: collections.defaultdict(dict)
        )

    def add_vote(self, vote: VoteMsg) -> Optional[QC]:
        """
        Adds a vote and checks if a QC can be formed.
        Returns the new QC if formed, None otherwise.
        """
        # Store vote
        if vote.node_hash not in self.votes[vote.view_number]:
            self.votes[vote.view_number][vote.node_hash] = {}
        
        self.votes[vote.view_number][vote.node_hash][vote.sender] = vote.partial_sig
        
        # Check Threshold
        sigs = self.votes[vote.view_number][vote.node_hash]
        if len(sigs) >= (config.N - config.F):
            # Form QC
            qc = QC(
                type=vote.type,
                view_number=vote.view_number,
                node_hash=vote.node_hash,
                sig=QCSignature(signers=set(sigs.keys()))
            )
            logger.debug(f"Replica {self.my_id} aggregated QC for {vote.node_hash[:8]} in view {vote.view_number}")
            return qc
        
        return None
