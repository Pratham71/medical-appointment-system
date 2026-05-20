@echo off
setlocal enabledelayedexpansion
:: ── setup.bat ─────────────────────────────────────────────────────────────────
:: One-command Docker setup for the College Infirmary Appointment System.
:: Run once after cloning:  setup.bat
::
:: What it does:
::   1. Checks that Docker and Docker Compose are installed
::   2. Copies .env.example -> .env  (if .env doesn't exist yet)
::   3. Generates a secure random JWT_SECRET_KEY and writes it into .env
::   4. Prompts once for a MySQL root password and writes it into .env
::   5. Runs docker compose up --build -d
:: ─────────────────────────────────────────────────────────────────────────────

echo.
echo === College Infirmary - Docker Setup ===
echo.

:: ── 1. Prerequisite checks ───────────────────────────────────────────────────
echo Checking prerequisites:

where docker >nul 2>&1
if errorlevel 1 (
    echo   [ERR] Docker is not installed. Get it at https://docs.docker.com/get-docker/
    goto :fail
)

:: Print Docker version (equivalent to bash awk + tr to strip trailing comma)
for /f "tokens=3 delims= " %%v in ('docker --version') do (
    set DOCKER_VER=%%v
    set DOCKER_VER=!DOCKER_VER:,=!
    goto :docker_ver_done
)
:docker_ver_done
echo   [OK] docker !DOCKER_VER!

:: Support both 'docker compose' (v2 plugin) and 'docker-compose' (v1 standalone)
set COMPOSE=
docker compose version >nul 2>&1
if not errorlevel 1 (
    set COMPOSE=docker compose
    goto :compose_found
)
where docker-compose >nul 2>&1
if not errorlevel 1 (
    set COMPOSE=docker-compose
    goto :compose_found
)
echo   [ERR] Docker Compose is not installed. Get it at https://docs.docker.com/compose/install/
goto :fail

:compose_found
echo   [OK] !COMPOSE!
echo.

:: ── 2. Create .env from template ─────────────────────────────────────────────
if exist ".env" (
    echo   [!!] .env already exists - skipping copy from .env.example
) else (
    copy /y ".env.example" ".env" >nul
    echo   [OK] Created .env from .env.example
)

:: ── 3. Generate JWT secret ────────────────────────────────────────────────────
:: Read current JWT value — grep equivalent using findstr + a temp file
set JWT_CURRENT=
for /f "tokens=2 delims==" %%v in ('findstr /b "JWT_SECRET_KEY=" .env') do set JWT_CURRENT=%%v

:: Strip any surrounding whitespace from the value
set JWT_CURRENT=!JWT_CURRENT: =!

if "!JWT_CURRENT!"=="" goto :gen_jwt
if "!JWT_CURRENT!"=="change-this-dev-secret" goto :gen_jwt
echo   [OK] JWT_SECRET_KEY already set - keeping existing value
goto :jwt_done

:gen_jwt
:: Use PowerShell's cryptographic RNG — available on all Windows 10+ machines.
:: Generates 32 random bytes as a lowercase hex string (64 chars), identical
:: to what `openssl rand -hex 32` produces on Linux/macOS.
for /f %%s in ('powershell -NoProfile -Command ^
    "$bytes = New-Object byte[] 32; ^
     (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); ^
     [BitConverter]::ToString($bytes).Replace('-','').ToLower()"') do set JWT_SECRET=%%s

call :replace_env_line "JWT_SECRET_KEY=" "JWT_SECRET_KEY=!JWT_SECRET!"
echo   [OK] Generated JWT_SECRET_KEY

:jwt_done

:: ── 4. MySQL password ─────────────────────────────────────────────────────────
set PW_CURRENT=
for /f "tokens=2 delims==" %%v in ('findstr /b "MYSQL_PASSWORD=" .env') do set PW_CURRENT=%%v
set PW_CURRENT=!PW_CURRENT: =!

if not "!PW_CURRENT!"=="" (
    echo   [OK] MYSQL_PASSWORD already set - keeping existing value
    goto :pw_done
)

echo   Enter a MySQL root password for the local Docker database.
echo   This is only used inside Docker - any value works for local dev.
echo.

:: PowerShell Read-Host -AsSecureString masks input (dots instead of chars),
:: then converts back to plaintext for writing into .env.
:: This is the Windows equivalent of bash's `read -rsp`.
for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command ^
    "$s = Read-Host '  Password' -AsSecureString; ^
     $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); ^
     [Runtime.InteropServices.Marshal]::PtrToStringAuto($b)"`) do set MYSQL_PW=%%p

if "!MYSQL_PW!"=="" (
    echo   [ERR] MySQL password cannot be empty.
    goto :fail
)

call :replace_env_line "MYSQL_PASSWORD=" "MYSQL_PASSWORD=!MYSQL_PW!"
echo   [OK] MYSQL_PASSWORD written to .env

:pw_done
echo.

:: ── 5. Start containers ───────────────────────────────────────────────────────
echo Building and starting containers (this takes a few minutes the first time):
echo.
!COMPOSE! up --build -d
if errorlevel 1 (
    echo   [ERR] docker compose failed. Check the output above for details.
    goto :fail
)

echo.
echo   [OK] All containers are up
echo.
echo === Setup complete ===
echo.
echo   Frontend  -^>  http://localhost:3000
echo   Backend   -^>  http://localhost:8000
echo   API docs  -^>  http://localhost:8000/docs
echo.
echo Seed accounts (password: password123):
echo   Student          student@college.edu
echo   Professor        professor@college.edu
echo   College Staff    college.staff@college.edu
echo   Hostel Staff     hostel.staff@college.edu
echo   Doctor           doctor@college.edu
echo   Staff            staff@college.edu
echo   Admin            admin@college.edu
echo.
echo To stop:               !COMPOSE! down
echo To reset the database:  !COMPOSE! down -v  (deletes all data)
echo.
goto :eof

:: ── Helper: replace a line in .env in-place ───────────────────────────────────
:: Usage: call :replace_env_line "KEY=" "KEY=newvalue"
:: Rewrites .env to a temp file, replacing any line starting with %~1,
:: then moves the temp file back over .env.
:replace_env_line
:: %~1 = the KEY= prefix to match (e.g. "JWT_SECRET_KEY=")
:: %~2 = the full replacement line  (e.g. "JWT_SECRET_KEY=abc123")
set "_prefix=%~1"
set "_newline=%~2"
set "_prefixlen=0"
set "_tmp=%TEMP%\env_rewrite_%RANDOM%.tmp"
:: Count the length of the prefix string so we can slice lines for comparison.
:: We match !_line:~0,N! == _prefix which includes the '=' — no false prefix hits.
set "_counter=!_prefix!"
:count_loop
if not "!_counter!"=="" (
    set /a _prefixlen+=1
    set "_counter=!_counter:~1!"
    goto :count_loop
)
(
    for /f "usebackq delims=" %%L in (".env") do (
        set "_line=%%L"
        if "!_line:~0,%_prefixlen%!"=="!_prefix!" (
            echo !_newline!
        ) else (
            echo %%L
        )
    )
) > "!_tmp!"
move /y "!_tmp!" ".env" >nul
goto :eof

:fail
echo.
echo Setup did not complete. Fix the error above and run setup.bat again.
echo.
endlocal
exit /b 1
