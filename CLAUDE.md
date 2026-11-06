# harborlight-apps.github.io: публичные страницы политики и поддержки

Это публичный репозиторий (GitHub Pages). Здесь только публичное: никаких секретов, личных данных и внутренних заметок.

- Страницы `astir/privacy` и `astir/support` собираются **только** командой `python3 tools/build.py <политика.md> --set=PUBLISHER_NAME=... --set=EFFECTIVE_DATE=...`; руками HTML не правим.
- Текст политики живёт в `architect/docs/apps/alarm-clock-privacy-policy.md`, значения имени и контактов — в `architect/docs/publisher-identity.json`. Строку «Publisher» берём из него (`policy_publisher_format`).
- **Менять или публиковать политику, имя издателя и контакты можно только по слову владельца.** Не удалять и не переписывать политику по своей инициативе; любая правка — через исходный текст в `architect` и сборку.
- После сборки: `python3 ../architect/tools/check-identity.py` должен быть без FAIL. Коммит и пуш в `main` в конце задачи.
