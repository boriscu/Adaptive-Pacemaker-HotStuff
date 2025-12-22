"""
ReplicaState model.

Represents the observable state of a replica for UI serialization.
Used for displaying replica information in the visualization.
"""

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.phase_type import PhaseType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate


class ReplicaState(BaseModel):
    """
    Snapshot of a replica's state for visualization and serialization.
    
    This model captures all the key state variables from a replica
    that should be displayed in the UI or exported in experiment results.
    """
    
    replica_id: ReplicaId = Field(
        description="Unique identifier of this replica"
    )
    current_view: ViewNumber = Field(
        description="Current view number (curView in paper)"
    )
    current_phase: PhaseType = Field(
        description="Current phase within the view"
    )
    is_leader: bool = Field(
        description="Whether this replica is the leader for current view"
    )
    is_faulty: bool = Field(
        default=False,
        description="Whether this replica has been marked as faulty"
    )
    fault_type: FaultType = Field(
        default=FaultType.NONE,
        description="Type of fault if faulty"
    )
    locked_qc: Optional[QuorumCertificate] = Field(
        default=None,
        description="The locked QC (lockedQC in paper)"
    )
    prepare_qc: Optional[QuorumCertificate] = Field(
        default=None,
        description="The prepare QC (prepareQC/highQC in paper)"
    )
    pending_block: Optional[Block] = Field(
        default=None,
        description="Currently proposed block awaiting votes"
    )
    committed_block_hashes: List[BlockHash] = Field(
        default_factory=list,
        description="List of committed block hashes"
    )
    last_voted_view: Optional[ViewNumber] = Field(
        default=None,
        description="Last view in which this replica voted"
    )
