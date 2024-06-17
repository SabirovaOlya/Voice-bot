from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func, desc
from database.models import User, District, Street, Part, Voice
from typing import List
from enum import Enum


class Role(Enum):
    admin = 'admin'
    user = 'user'


class UserManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_admin(self, user_id: str) -> bool:
        user = await self.get_user_by_user_id(user_id)
        if user:
            print(user.role.value == 'admin')
            return user.role.value == 'admin'
        return False

    async def add_user(self, full_name: str, user_id: str, username: str, role: str = 'user') -> User:
        user = User(
            full_name=full_name,
            user_id=user_id,
            username=username,
            role=role
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, id: int) -> User:
        result = await self.session.execute(select(User).filter(User.id == id))
        return result.scalar_one_or_none()

    async def get_user_by_user_id(self, user_id: str) -> User:
        result = await self.session.execute(select(User).filter(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def update_user_username(self, user_id: str, new_username: str) -> User:
        user = await self.session.execute(select(User).filter(User.user_id == user_id)).scalar_one()
        user.username = new_username
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: str) -> bool:
        user = await self.session.execute(select(User).filter(User.user_id == user_id)).scalar_one_or_none()
        if user:
            self.session.delete(user)
            await self.session.commit()
            return True
        return False


class DistrictManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_district(self, name: str) -> District:
        district = District(name=name)
        self.session.add(district)
        await self.session.commit()
        await self.session.refresh(district)
        return district

    async def get_district_by_id(self, district_id: int) -> District:
        return await self.session.execute(select(District).filter(District.id == district_id)).scalar_one_or_none()

    async def get_all_districts(self) -> List[District]:
        result = await self.session.execute(
            select(District)
            .order_by(District.name)
        )
        districts = result.scalars().all()
        return districts

    async def update_district_name(self, district_id: int, new_name: str) -> District:
        district = await self.session.execute(select(District).filter(District.id == district_id)).scalar_one()
        district.name = new_name
        await self.session.commit()
        await self.session.refresh(district)
        return district

    async def delete_district(self, district_id: int) -> bool:
        district = await self.session.execute(select(District).filter(District.id == district_id)).scalar_one_or_none()
        if district:
            self.session.delete(district)
            await self.session.commit()
            return True
        return False


class StreetManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_street(self, name: str, district_id: int) -> Street:
        street = Street(name=name, district_id=district_id)
        self.session.add(street)
        await self.session.commit()
        await self.session.refresh(street)
        return street

    async def get_street_by_id(self, street_id: int) -> Street:
        try:
            result = await self.session.execute(select(Street).filter(Street.id == street_id))
            street = result.scalars().one_or_none()
            if not street:
                raise NoResultFound(f"No street found with id {street_id}")
            return street
        except Exception as e:
            raise e

    async def update_street_name(self, street_id: int, new_name: str) -> Street:
        street = await self.get_street_by_id(street_id)
        street.name = new_name
        await self.session.commit()
        await self.session.refresh(street)
        return street

    async def delete_street(self, street_id: int) -> bool:
        street = await self.get_street_by_id(street_id)
        if street:
            await self.session.delete(street)
            await self.session.commit()
            return True
        return False

    async def get_all_streets(self) -> List[Street]:
        result = await self.session.execute(select(Street))
        streets = result.scalars().all()
        return streets

    async def get_streets_by_district_id(self, district_id: int) -> List[Street]:
        result = await self.session.execute(
            select(Street)
            .filter(Street.district_id == district_id)
            .order_by(Street.name)
        )
        streets = result.scalars().all()
        return streets


class PartManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_part_by_id(self, part_id: int) -> Part:
        try:
            result = await self.session.execute(select(Part).filter(Part.id == part_id))
            part = result.scalars().one_or_none()
            if not part:
                raise NoResultFound(f"No part found with id {part_id}")
            return part
        except Exception as e:
            raise e

    async def get_available_parts(self) -> Part:
        result = await self.session.execute(
            select(Part)
            .filter(Part.is_available == True)
        )
        part = result.scalars().one_or_none()
        return part

    async def update_part_status(self, part_id: int, status: bool) -> bool:
        try:
            part = await self.get_part_by_id(part_id)
            part.is_available = status
            await self.session.commit()
            await self.session.refresh(part)
            return True
        except Exception as e:
            print(e)
            return False


class VoiceManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_voice(self, user_id: str, street_id: int, part_id: int) -> Voice:
        voice = Voice(
            user_id=user_id,
            street_id=street_id,
            part_id=part_id
        )
        self.session.add(voice)
        await self.session.commit()
        await self.session.refresh(voice)
        return voice

    async def get_voice_by_userid(self, user_id: str, part_id: int) -> Voice:
        result = await self.session.execute(select(Voice).filter_by(user_id=user_id, part_id=part_id))
        return result.scalar_one_or_none()

    async def update_voice_status(self, user_id: str, status: bool, part_id: int) -> bool:
        try:
            voice = await self.get_voice_by_userid(user_id, part_id)
            voice.is_active = status
            await self.session.commit()
            await self.session.refresh(voice)
            return True
        except Exception as e:
            print(e)
            return False

    async def get_voice_by_user_id(self, user_id: str, part_id: int):
        result = await self.session.execute(
            select(Voice.id, Voice.user_id, Part.name, Street.name, District.name, Voice.is_active)
            .join(Part, Voice.part_id == Part.id)
            .join(Street, Voice.street_id == Street.id)
            .join(District, Street.district_id == District.id)
            .filter(Voice.user_id == user_id)
            .filter(Voice.part_id == part_id)
        )
        row = result.first()

        if row is None:
            return None

        voice_id, user_id, part_name, street_name, district_name, is_active = row
        return {
            "voice_id": voice_id,
            "user_id": user_id,
            "part_name": part_name,
            "street_name": street_name,
            "district_name": district_name,
            "is_active": is_active
        }

    async def get_voice_by_street_id(self, street_id: int, part_id: int) -> List[User]:
        result = await self.session.execute(
            select(Voice)
            .filter(Voice.street_id == street_id)
            .filter(Voice.part_id == part_id)
            .filter(Voice.is_active == True)
        )
        return result.scalars().all()

    async def get_voices_by_district_id(self, district_id: int, part_id: int) -> List[Voice]:
        result = await self.session.execute(
            select(Voice).join(Street)
            .filter(Street.district_id == district_id)
            .filter(Voice.part_id == part_id)
            .filter(Voice.is_active == True)
        )
        return result.scalars().all()

    async def get_all_voices(self):
        result = await self.session.execute(select(Voice))
        return result.scalars().all()

    async def get_street_ranking(self, street_id: int, part_id: int):
        result = await self.session.execute(
            select(
                Street.id,
                func.count(Voice.id).label('voice_count')
            )
            .join(Voice, Voice.street_id == Street.id)
            .filter(Voice.part_id == part_id)
            .group_by(Street.id)
            .order_by(desc('voice_count'))
        )
        street_rankings = result.all()

        rank = next((i + 1 for i, row in enumerate(street_rankings) if row.id == street_id), None)
        return rank

    async def get_district_ranking(self, district_id: int, part_id: int):
        result = await self.session.execute(
            select(
                District.id,
                func.count(Voice.id).label('voice_count')
            )
            .join(Street, Street.district_id == District.id)
            .join(Voice, Voice.street_id == Street.id)
            .filter(Voice.part_id == part_id)
            .group_by(District.id)
            .order_by(desc('voice_count'))
        )
        district_rankings = result.all()

        rank = next((i + 1 for i, row in enumerate(district_rankings) if row.id == district_id), None)
        return rank

    async def get_voice_statistics(self, user_id: str, part_id: int):
        result = await self.session.execute(
            select(
                Voice.id,
                Voice.street_id,
                Street.district_id
            )
            .join(Street, Voice.street_id == Street.id)
            .filter(Voice.user_id == user_id)
            .filter(Voice.part_id == part_id)
        )
        voice = result.first()
        if voice is None:
            return None

        voice_id, street_id, district_id = voice

        street_rank = await self.get_street_ranking(street_id, part_id)
        district_rank = await self.get_district_ranking(district_id, part_id)

        return {
            "voice_id": voice_id,
            "street_rank": street_rank,
            "district_rank": district_rank
        }

    async def get_district_statistics(self, part_id: int):
        result = await self.session.execute(
            select(
                District.id,
                District.name,
                func.count(Voice.id).label('voice_count')
            )
            .join(Street, Street.district_id == District.id)
            .join(Voice, Voice.street_id == Street.id)
            .filter(Voice.part_id == part_id)
            .group_by(District.id)
            .order_by(desc('voice_count'))
        )
        district_rankings = result.all()

        statistics = []
        for i, row in enumerate(district_rankings):
            district_id, district_name, voice_count = row
            rank = i + 1
            statistics.append({
                "district_id": district_id,
                "district_name": district_name,
                "voice_count": voice_count,
                "rank": rank
            })

        return statistics

    async def get_street_statistics(self, part_id: int, district_id: int):
        # Get the count of voices per street within a specific district, ordered by the count in descending order
        result = await self.session.execute(
            select(
                Street.name,
                func.count(Voice.id).label('voice_count')
            )
            .join(District, Street.district_id == District.id)
            .join(Voice, Voice.street_id == Street.id)
            .filter(Voice.part_id == part_id)
            .filter(Street.district_id == district_id)
            .group_by(Street.id)
            .order_by(desc('voice_count'))
        )
        street_rankings = result.all()

        # Assign ranks to each street
        statistics = []
        for i, row in enumerate(street_rankings):
            street_name, voice_count = row
            rank = i + 1  # Ranking starts from 1
            statistics.append({
                "street_name": street_name,
                "voice_count": voice_count,
                "rank": rank
            })

        return statistics
