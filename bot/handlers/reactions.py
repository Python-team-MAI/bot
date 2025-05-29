from aiogram import Router, F
from aiogram.types import MessageReactionUpdated
from bot.handlers.on_click.main_menu import on_reaction_added, on_reaction_removed
from bot.dialogs.main_menu.states import MainMenu

router = Router(name="reactions")

@router.message_reaction(MainMenu.start_question)
async def handle_reaction_update(event: MessageReactionUpdated):
    """Handle both adding and removing reactions"""
    if not event.message.from_user.is_bot:
        return

    reaction = event.reaction.emoji
    print(reaction)
    if reaction not in ["👍", "👎"]:
        return

    if event.old_reaction and event.old_reaction.emoji == reaction:
        await on_reaction_removed(event.message, reaction)
    else:
        await on_reaction_added(event.message, reaction) 