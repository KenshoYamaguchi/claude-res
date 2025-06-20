@echo off
echo コワーキングスペース予約システムを起動しています...
echo.

REM Flaskアプリケーションの起動
python app.py

REM エラーが発生した場合の処理
if %ERRORLEVEL% neq 0 (
    echo.
    echo エラーが発生しました。
    echo - Pythonがインストールされているか確認してください
    echo - 必要なパッケージ（Flask）がインストールされているか確認してください
    echo - pip install flask
    echo.
    pause
    exit /b 1
)

echo.
echo サーバーが停止しました。
pause