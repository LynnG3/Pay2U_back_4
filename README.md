# Pay2U_back_4
MVP Pay2U - все подписки в одном приложении

## ToDo:
#### эндпойнты:
/services Развлекательные сервисы;
/sell-history История покупок;
/subscriptions Мои подписки;
/catalog Каталог подписок;
/manage-subcription Управление подпиской;
/movie Кино;
##### лучше заменить на категории - кино, книги, музыка
/connect-subcription Подключение подписки;
/payment Оплата подписки;
/auto-payment Подключение автоплатежа;

#### приложения:
юзерс(в конце решить че с ними)
сервисы
оплата
#### модели, сериалайзеры, вью - список где какие методы реализовать:

#### доп фичи:

- генератор промокода
- фильтрация по отзывам и чему-то еще 
- пуш уведомления (срок подписки истекает через 3 дня, что-то еще) - Бизнес логика - нужно инфо от ба, куда должны перекидывать 
пушуведомления, что после них надо сделать
- юзеры Интеграция с япаспортом - хз как это, в конце разобраться или JWT токен хз работает ли


#### служебное:
- Настроить селери чтоб раз в день или раз в 12 часов (?)проверять подписки и тд актуальность
В подписках какие-то поля список предупреждений сроки итд
- тесты - разобраться с библиотекой factory_boy
- добавить папку со фронтом позже
- контейнеры - докерфайлы в тч и для фронта
- нгинкс - ждем ответ по серверу, если дадут тестовый хорошо, если нет ищем бесплатный или тестируем на локалке
- интеграция с sentry, логирование ошибок
