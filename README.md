# Project: Flask + Nginx + K8s + ArgoCD 🚀

## 📝 Описание проекта
Данный проект представляет собой полностью автоматизированный процесс развертывания (GitOps) веб-приложения на базе Flask. 
Приложение работает в связке с базой данных (PostgreSQL), кэшем (Redis) и системой мониторинга (Prometheus). Инфраструктура упакована в Docker, разворачивается в локальном кластере Minikube с помощью Ansible и управляется автоматически через ArgoCD.

## 🏗 Структура репозитория
* `app/` — Исходный код приложения (Flask-API).
* `docker/` — Конфиги для сборки Docker-образа (настройка Nginx, скрипт запуска Gunicorn) и сам `Dockerfile`.
* `helm/` — Helm-чарты, разделенные на 3 логических модуля:
  * `app-chart` — Веб-приложение (Flask + Nginx).
  * `db-chart` — Хранилища данных (Postgres + Redis).
  * `monitoring-chart` — Мониторинг (Prometheus).
* `ansible/` — Playbook для автоматической установки и настройки кластера Minikube.
* `argocd-apps.yaml` — Декларативное описание приложений для ArgoCD.

## ⚙️ Архитектурные решения (DoD)
1. **Единый контейнер (Unix Socket):** Приложение (Gunicorn) и веб-сервер (Nginx) работают в одном Docker-контейнере. Общение между ними настроено через быстрый Unix-сокет (`/tmp/app.sock`), а не по сети.
2. **Инфраструктура как код (IaC):** Kubernetes-кластер поднимается "с нуля" без ручного вмешательства. Написан Ansible-плейбук, который автоматически скачивает и запускает Minikube.
3. **GitOps подход:** Деплой происходит через ArgoCD. Система следит за веткой `main` этого репозитория и автоматически применяет изменения Helm-чартов в кластер.

## 🚀 Инструкция по запуску

**1. Поднятие кластера (Ansible)**
```bash
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

**2. Установка ArgoCD**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f [https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml](https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml)
```

**3. Запуск GitOps деплоя**
Применяем манифест, который укажет ArgoCD вытянуть и развернуть Helm-чарты из этого репозитория:
```bash
kubectl apply -f argocd-apps.yaml
```

После этого ArgoCD автоматически поднимет все необходимые Pods (БД, кэш, приложение и мониторинг). Проверить статус можно командой:
```bash
kubectl get pods -w
```
