# Button Tapper

Сервис для автоматического поиска и нажатия цветной кнопки в Android-приложении.

Скрипт:

1. подключается к Android-устройству через **ADB**;
2. запускает указанное приложение;
3. получает скриншоты экрана;
4. ищет кнопку заданного цвета с помощью **OpenCV**;
5. нажимает на центр найденной области;
6. продолжает поиск следующих кнопок;
7. завершает работу, если приложение закрыто.

## Требования

* Python `3.12`
* Android SDK Platform Tools (`adb`)
* Android-устройство с включённой USB/Wireless Debugging
* OpenCV

## Установка

```bash
make install
```

без `make`:

```bash
python -m pip install -e ".[dev]"
```

Проверить подключение устройства:

```bash
adb devices
```

Устройство должно иметь статус:

```text
device
```

## Запуск

Основной запуск:

```bash
make run PACKAGE=com.example.buttontest
```

Либо напрямую:

```bash
python src/main.py com.example.buttontest
```

Цвет кнопки можно изменить через аргумент:

```bash
python src/main.py com.example.buttontest --color red
```

Поддерживаются цвета:

```text
green
red
blue
yellow
orange
purple
```

Также можно указать собственный YAML-конфиг:

```bash
python src/main.py com.example.buttontest --config config.yml
```

## Demo

Для проверки детектора без Android-устройства используются подготовленные изображения:

```bash
make demo
```

Demo последовательно открывает изображения из:

```text
src/fixtures/images/
```

и показывает найденную область и координаты центра кнопки.
`enter` - переключать изображения

`q` или `Esc`, чтобы завершить demo.


### E2E-тесты

E2E-тесты требуют подключённого Android-устройства:

Перед запуском тестов необходимо установить тестовое Android-приложение.

Тестовое приложение находится в:

```text
android_apk/
```

Package:

```text
com.example.buttontest
```

Проверить установку:

```bash
adb shell pm list packages | grep buttontest
```

Если Android Studio используется для сборки приложения, его можно установить на устройство через:

```bash
adb install path/to/app-debug.apk
```

Если устройство не подключено, E2E-тесты автоматически пропускаются.
