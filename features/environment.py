"""
Behave environment setup
Configura contexto para tests de Behave
"""

from playwright.sync_api import sync_playwright


def before_all(context):
    """Se ejecuta antes de todos los tests"""
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    """Se ejecuta antes de cada scenario"""
    context.page = context.browser.new_page()
    context.page.set_viewport_size({"width": 1280, "height": 720})
    
    # Para guardar mensajes de consola
    context.console_messages = []
    
    def on_console_msg(msg):
        context.console_messages.append({
            "type": msg.type,
            "text": msg.text
        })
    
    context.page.on('console', on_console_msg)


def after_scenario(context, scenario):
    """Se ejecuta después de cada scenario"""
    if hasattr(context, 'page') and context.page:
        context.page.close()


def after_all(context):
    """Se ejecuta después de todos los tests"""
    if hasattr(context, 'browser') and context.browser:
        context.browser.close()
    
    if hasattr(context, 'playwright') and context.playwright:
        context.playwright.stop()
