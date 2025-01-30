from git import Repo
from datetime import datetime
from logs import get_logger
from src.params.config import config
from src.schemas.core_schemas import VersionInfo


logger = get_logger(__name__)


def get_latest_commit_info() -> VersionInfo | None:
    try:
        repo = Repo(search_parent_directories=True)
        version_info = VersionInfo(
            object_hash=repo.head.object.hexsha,
            object_type=repo.head.object.type,
            date=datetime.fromtimestamp(repo.head.object.authored_date, tz=config.time_zone_ino),
            author=repo.head.object.author.name,
            branch=repo.active_branch.name,
        )
    except Exception:
        logger.error('Error while getting latest commit info', exc_info=True)
        return None
    else:
        return version_info


