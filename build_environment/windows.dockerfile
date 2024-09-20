FROM mcr.microsoft.com/windows/servercore:ltsc2022

COPY setup_windows.ps1 /setup.ps1

RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; ./setup.ps1