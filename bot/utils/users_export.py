from __future__ import annotations
import csv
import io
from datetime import datetime, timezone

from aiogram.types import BufferedInputFile

from api.users.models import UsersOrm


async def convert_users_to_csv(users: list[UsersOrm]) -> BufferedInputFile:
    """Export all users in csv file."""
    columns = UsersOrm.__table__.columns
    data = [[getattr(user, column.name) for column in columns] for user in users]

    s = io.StringIO()
    csv.writer(s).writerow(columns)
    csv.writer(s).writerows(data)
    s.seek(0)

    return BufferedInputFile(
        file=s.getvalue().encode("utf-8"),
        filename=f"users_{datetime.now(timezone.utc).strftime('%Y.%m.%d_%H.%M')}.csv",
    )
