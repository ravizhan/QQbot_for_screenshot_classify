import nonebot
from nonebot.adapters.onebot import V11Adapter as onebotAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(onebotAdapter)

nonebot.load_plugin("plugins.screenshot")

if __name__ == "__main__":
    nonebot.run()
