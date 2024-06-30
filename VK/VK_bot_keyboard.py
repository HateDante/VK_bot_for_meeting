from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_vk_keyboard(text_event):
    vk_keyboard = VkKeyboard()
    if text_event == 'prepare_buttons':
        vk_keyboard.add_button('Погнали', VkKeyboardColor.POSITIVE)
    elif text_event == 'start_buttons':
        vk_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
    elif text_event == 'find_buttons':
        vk_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        vk_keyboard.add_button('Добавить в избранное', VkKeyboardColor.POSITIVE)
        vk_keyboard.add_line()
        vk_keyboard.add_button('Избранное', VkKeyboardColor.SECONDARY)
        vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)
    elif text_event == 'end_buttons':
        vk_keyboard.add_button('Закончить', VkKeyboardColor.NEGATIVE)

    return vk_keyboard.get_keyboard()
