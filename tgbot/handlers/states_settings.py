import os
from aiogram import types, Router, Bot, F
from aiogram.fsm.context import FSMContext

import zipfile
import rarfile
import shutil
from pathlib import Path

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message

from utils import (
    is_golden_key_valid,
    is_user_agent_valid,
    is_proxy_valid, 
    is_proxy_working
)


router = Router()


@router.message(states.SettingsStates.waiting_for_golden_key, F.text)
async def handler_waiting_for_golden_key(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not is_golden_key_valid(message.text.strip()):
            raise Exception("❌ Неверный формат Golden Key. Пример: bzhzi9n5x9y1xaaa9j48kp6bu4671xxy")

        config = sett.get("config")
        config["funpay"]["api"]["golden_key"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(f"✅ <b>Golden Key</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_user_agent, F.text)
async def handler_waiting_for_user_agent(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not is_user_agent_valid(message.text.strip()):
            raise Exception("❌ Неверный формат User Agent. Пример: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")

        config = sett.get("config")
        config["funpay"]["api"]["user_agent"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(f"✅ <b>User Agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_fp_proxy, F.text)
async def handler_waiting_for_fp_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_proxy_valid(message.text.strip()):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(message.text.strip()):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к funpay.com")

        config = sett.get("config")
        config["funpay"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(f"✅ <b>Прокси для FunPay</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_tg_proxy, F.text)
async def handler_waiting_for_tg_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_proxy_valid(message.text.strip()):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(message.text.strip(), "https://api.telegram.org/"):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к api.telegram.org")

        config = sett.get("config")
        config["telegram"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(f"✅ <b>Прокси для Telegram</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.auth_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_requests_timeout, F.text)
async def handler_waiting_for_requests_timeout(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["api"]["requests_timeout"] = int(message.text.strip())
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_runner_requests_delay, F.text)
async def handler_waiting_for_runner_requests_delay(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["api"]["runner_requests_delay"] = int(message.text.strip())
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.conn_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="conn").pack())
        )
            

@router.message(states.SettingsStates.waiting_for_notifications_chat_id, F.text)
async def handler_waiting_for_notifications_chat_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None) 
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        
        if message.text.strip().isdigit(): 
            chat_id = "-100" + str(message.text.strip()).replace("-100", "")
        else: 
            chat_id = "@" + str(message.text.strip()).replace("@", "")

        config = sett.get("config")
        config["funpay"]["notifications"]["chat_id"] = chat_id
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.notifications_float_text(f"✅ <b>ID чата для логов</b> было успешно изменено на <b>{chat_id}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="notifications").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.notifications_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="notifications").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_orders_per_ticket, F.text)
async def handler_waiting_for_auto_tickets_orders_per_ticket(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["orders_per_ticket"] = int(message.text.strip())
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(f"✅ <b>Кол-во заказов в одном тикете</b> было успешно изменено на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_min_order_age, F.text)
async def handler_waiting_for_auto_tickets_min_order_age(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["min_order_age"] = int(message.text.strip())
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(f"✅ <b>Мин. возраст заказов</b> был успешно изменён на <b>{message.text.strip()} сек.</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_tickets_create_interval, F.text)
async def handler_waiting_for_auto_tickets_create_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["funpay"]["auto_tickets"]["interval"] = int(message.text.strip())
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(f"✅ <b>Интервал создания тикетов</b> был успешно изменён на <b>{message.text.strip()} сек.</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.tickets_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="tickets").pack())
        )


@router.message(states.SettingsStates.waiting_for_watermark_value, F.text)
async def handler_waiting_for_watermark_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 150:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["funpay"]["watermark"]["value"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="other").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
             message=message,
            text=templ.other_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="other").pack())
        )


@router.message(states.SettingsStates.waiting_for_logs_max_file_size, F.text)
async def handler_waiting_for_logs_max_file_size(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        max_size = message.text.strip()
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        max_size = int(max_size)

        config = sett.get("config")
        config["logs"]["max_file_size"] = max_size
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(f"✅ <b>Максимальный размер файла логов</b> был успешно изменён на <b>{max_size} MB</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )


@router.message(states.SettingsStates.waiting_for_new_fast_reply_text, F.text)
async def handler_waiting_for_new_fast_reply_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        text = message.text

        data = await state.get_data()
        last_page = data.get("last_page", 0)

        fast_replies = sett.get("fast_replies")
        fast_replies.append(text)
        sett.set("fast_replies", fast_replies)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(f"✅ <b>Быстрый ответ</b> успешно добавлен: <blockquote>{text}</blockquote>"),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(e), 
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
            

@router.message(states.SettingsStates.waiting_for_fast_reply_text, F.text)
async def handler_waiting_for_fast_reply_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        text = message.text

        data = await state.get_data()
        index = data.get("fast_reply_index")
        last_page = data.get("last_page", 0)

        fast_replies = sett.get("fast_replies")
        fast_replies[index] = text
        sett.set("fast_replies", fast_replies)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(f"✅ <b>Текст авто-ответ</b> был успешно изменён на: <blockquote>{text}</blockquote>"),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_fast_reply_text(e), 
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )


@router.message(
    states.SettingsStates.waiting_for_module_file, 
    F.document.file_name.lower().regexp(r'.*\.(zip|rar)$')
)
async def handler_waiting_for_module_file(message: types.Message, state: FSMContext, bot: Bot):
    try:
        await state.set_state(None)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        file_name = message.document.file_name
        temp_path = os.path.join("temp", file_name)
        modules_path = "modules"

        os.makedirs("temp", exist_ok=True)
        os.makedirs(modules_path, exist_ok=True)

        await bot.download(message.document, destination=temp_path)

        def _get_module_meta(dest):
            try:
                import ast

                constants = {}
                target_keys = {'NAME', 'DESCRIPTION', 'VERSION'}

                for py_file in Path(dest).rglob('*.py'):
                    if len(constants) == len(target_keys):
                        break
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name) and target.id in target_keys:
                                        try:
                                            constants[target.id] = ast.literal_eval(node.value)
                                        except:
                                            pass
                    except:
                        pass

                name = constants.get('NAME')
                description = constants.get('DESCRIPTION')
                version = constants.get('VERSION')
                
                return name, description, version
            except Exception as e:
                raise Exception(f"❌ Ошибка при инициализации модуля {os.path.basename(dest)}: <blockquote>{e}</blockquote>")

        if file_name.lower().endswith('.zip'):
            archive = zipfile.ZipFile(temp_path)
            names = archive.namelist()
        else:
            archive = rarfile.RarFile(temp_path)
            names = archive.namelist()

        with archive:
            has_init = any(
                n == f"{next(iter({n.split('/')[0] for n in names if '/' in n}))}//__init__.py"
                for n in names
            )

            # корневые папки в архиве
            root_folders = {n.split('/')[0] for n in names if '/' in n}
            single_folder = len(root_folders) == 1

            if has_init or single_folder:
                if has_init:
                    module_name = os.path.splitext(file_name)[0]
                    dest = os.path.join(modules_path, module_name)
                    os.makedirs(dest, exist_ok=True)
                    archive.extractall(dest)
                else:  # single_folder
                    module_name = next(iter(root_folders))
                    dest = os.path.join(modules_path, module_name)
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    archive.extractall(modules_path)  # распаковываем прямо в modules

                name, desc, version = _get_module_meta(dest)

                await throw_float_message(
                    state=state,
                    message=message,
                    text=templ.modules_float_text(
                        f"✅ Модуль <b>успешно импортирован</b>:"
                        f"\n\n<blockquote><b>{name} ({version})</b>"
                        f"\n{desc}</blockquote>"
                        f"\n\n❗ Для подключения <b>необходима перезагрузка</b> — /restart"
                    ),
                    reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
                )
            else:
                # каждую корневую папку из архива кладём в modules
                before = set(os.listdir(modules_path))
                extract_temp = os.path.join("temp", "extracted")
                os.makedirs(extract_temp, exist_ok=True)
                archive.extractall(extract_temp)

                for item in os.listdir(extract_temp):
                    src = os.path.join(extract_temp, item)
                    dst = os.path.join(modules_path, item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.move(src, dst)

                shutil.rmtree(extract_temp)
                after = set(os.listdir(modules_path))
                added_modules = {os.path.basename(f) for f in after - before}

                modules_info = []
                for mod_folder in added_modules:
                    mod_dest = os.path.join(modules_path, mod_folder)
                    name, desc, version = _get_module_meta(mod_dest)
                    modules_info.append((name or mod_folder, desc, version))

                str_added = "\n".join(
                    f"・ <b>{n}</b> ({v})" if v else f"・ <b>{n}</b>"
                    for n, d, v in modules_info
                )

                await throw_float_message(
                    state=state,
                    message=message,
                    text=templ.modules_float_text(
                        f"✅ Успешно импортировано <b>{len(added_modules)} модулей</b>:"
                        f"\n\n<blockquote>{str_added}</blockquote>"
                        f"\n\n❗ Для подключения <b>необходима перезагрузка</b> — /restart"
                    ),
                    reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
                )
        
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.modules_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )
    finally:
        try: os.remove(temp_path)
        except: pass