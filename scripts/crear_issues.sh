#!/usr/bin/env bash
# Crea issues a partir de PLAN_SDD.md. No mantiene un segundo catálogo de tareas.
# Compatible con Bash 3.2 y Python 3 (solo biblioteca estándar).
# Prueba local: DRY_RUN=1 bash scripts/crear_issues.sh
# Publicación: definir GH_USER_A/B/C y autenticar gh; el repo debe estar sin issues.
set -euo pipefail
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$SCRIPT_ROOT" "$@" <<'PY'
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
PLAN = Path('docs/02_planificacion/PLAN_SDD.md')
FICHAS = {
    'A': 'docs/04_integrantes/A/TAREAS_A.md',
    'B': 'docs/04_integrantes/B/TAREAS_B.md',
    'C': 'docs/04_integrantes/Angel_Zambrano/TAREAS_C.md',
}
NAMES = {'A': 'A', 'B': 'B', 'C': 'Angel Zambrano'}
MODELS = [('LR', 'A', 'logreg', '02'), ('RF', 'B', 'rf', '03'), ('XG', 'C', 'xgb', '04')]
LABELS = {
    'persona-A': ('1f77b4', 'Responsable: A'),
    'persona-B': ('2ca02c', 'Responsable: B'),
    'persona-C': ('ff7f0e', 'Responsable: Angel Zambrano'),
    'equipo': ('7f7f7f', 'Tarea conjunta'),
    'etl': ('d62728', 'Proceso ETL'),
    'base-compartida': ('bcbd22', 'Componentes comunes y persistencia'),
    'infra': ('8c8c8c', 'Repositorio y CI'),
    'viz': ('17becf', 'Visualización y dashboard'),
    'comparacion': ('2ca02c', 'Comparación de modelos'),
    'modelo-logreg': ('9467bd', 'Logistic Regression'),
    'modelo-rf': ('8c564b', 'Random Forest'),
    'modelo-xgb': ('e377c2', 'XGBoost: Angel Zambrano'),
}


def clean(value):
    return value.replace('**', '').replace('`', '').strip()


def read_tasks():
    tasks, phase = {}, None
    for line in (ROOT / PLAN).read_text(encoding='utf-8').splitlines():
        heading = re.match(r'^### (Fase \d+)\s*[—-]\s*(.+)', line)
        if heading:
            title = re.sub(r'\s*\([^)]*\)', '', heading[2]).strip()
            phase = heading[1] + ' - ' + title
        if not phase or not line.startswith('|'):
            continue
        cells = [clean(c) for c in line.strip().strip('|').split('|')]
        if not re.fullmatch(r'(?:T|ETL|DB|MC|VIZ|CMP|V|F|X)-\d+', cells[0]):
            continue
        if cells[0].startswith('X-'):
            if len(cells) != 4:
                raise ValueError('Fila de modelo inválida: ' + line)
            models = MODELS
        else:
            if len(cells) != 5:
                raise ValueError('Fila de tarea inválida: ' + line)
            models = [(None, None, None, None)]
        for prefix, person, model, notebook in models:
            if prefix:
                task_id = cells[0].replace('X-', prefix + '-')
                title = '[' + model + '] ' + cells[1]
                owners, deps, deliverable = [person], cells[2], cells[3]
                deps = re.sub(r'\bX-', prefix + '-', deps)
                deliverable = deliverable.replace('<x>', model).replace('0N_', notebook + '_')
            else:
                task_id, title, owner_text, deps, deliverable = cells
                owners = owner_text.replace('Angel Zambrano', 'C').split('+')
            if task_id in tasks:
                raise ValueError('ID duplicado en el plan: ' + task_id)
            if any(owner not in NAMES for owner in owners):
                raise ValueError('Responsable desconocido: ' + ', '.join(owners))
            dependencies = re.findall(r'\b(?:T|ETL|DB|MC|VIZ|CMP|V|F|LR|RF|XG)-\d+\b', deps)
            tasks[task_id] = {'title': title, 'owners': owners, 'deps': dependencies,
                              'deliverable': deliverable, 'phase': phase}
    if not tasks:
        raise ValueError('No se encontraron tareas en el plan')
    visited, active = set(), set()
    def visit(task_id):
        if task_id not in tasks:
            raise ValueError('Dependencia inexistente: ' + task_id)
        if task_id in active:
            raise ValueError('Dependencias circulares: ' + task_id)
        if task_id in visited:
            return
        active.add(task_id)
        for dependency in tasks[task_id]['deps']:
            visit(dependency)
        active.remove(task_id)
        visited.add(task_id)
    for task_id in tasks:
        visit(task_id)
    return tasks


def labels_for(task_id, task):
    labels = ['persona-' + person for person in task['owners']]
    prefix = task_id.split('-')[0]
    topic = {'ETL': 'etl', 'DB': 'base-compartida', 'MC': 'base-compartida',
             'VIZ': 'viz', 'V': 'viz', 'CMP': 'comparacion',
             'LR': 'modelo-logreg', 'RF': 'modelo-rf', 'XG': 'modelo-xgb'}.get(prefix)
    if topic:
        labels.append(topic)
    if task_id in ('T-00', 'T-15'):
        labels.append('infra')
    if task_id == 'F-1':
        labels.append('base-compartida')
    if task_id == 'CMP-3':
        labels.append('viz')
    if len(task['owners']) > 1:
        labels.append('equipo')
    return labels


def gh(*args):
    result = subprocess.run(['gh', *args], check=False, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Falló gh: ' + args[0])
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description='Generar issues desde PLAN_SDD.md')
    parser.add_argument('--dry-run', action='store_true', help='validar y mostrar sin acceder a GitHub')
    args = parser.parse_args(sys.argv[2:])
    dry_env = os.environ.get('DRY_RUN', '0')
    if dry_env not in ('0', '1'):
        raise ValueError('DRY_RUN debe ser 0 o 1')
    tasks = read_tasks()
    for path in FICHAS.values():
        if not (ROOT / path).is_file():
            raise ValueError('Falta la ficha: ' + path)
    if args.dry_run or dry_env == '1':
        for task_id, task in tasks.items():
            owners = ', '.join(NAMES[p] for p in task['owners'])
            print('[dry-run] ' + task_id + ' | ' + owners + ' | ' + task['title'])
            print('  Depende de: ' + (', '.join(task['deps']) or 'nada'))
            print('  Entregable: ' + task['deliverable'])
        print('Modo de prueba: ' + str(len(tasks)) + ' tareas. Sin cambios en GitHub.')
        return
    users = {person: os.environ.get('GH_USER_' + person, '').strip() for person in NAMES}
    if not all(users.values()):
        raise ValueError('Definir GH_USER_A, GH_USER_B y GH_USER_C con usuarios reales de GitHub')
    if not shutil.which('gh'):
        raise ValueError('Falta gh; instalarlo y autenticarlo para publicar, o usar --dry-run')
    repo = json.loads(gh('repo', 'view', '--json', 'nameWithOwner,url'))
    if json.loads(gh('issue', 'list', '--state', 'all', '--limit', '1', '--json', 'number')):
        raise ValueError('El repo ya tiene issues. Revisar y completar los faltantes manualmente para no duplicarlos')
    for name, (color, description) in LABELS.items():
        gh('label', 'create', name, '--color', color, '--description', description, '--force')
    existing = set(gh('api', 'repos/' + repo['nameWithOwner'] + '/milestones',
                      '--paginate', '--jq', '.[].title').splitlines())
    for phase in dict.fromkeys(task['phase'] for task in tasks.values()):
        if phase not in existing:
            gh('api', 'repos/' + repo['nameWithOwner'] + '/milestones', '-f', 'title=' + phase)
    numbers = {}
    for task_id, task in tasks.items():
        owners = ', '.join(NAMES[p] for p in task['owners'])
        ficha = FICHAS[task['owners'][0]] if len(task['owners']) == 1 else str(PLAN)
        body = ('**ID:** ' + task_id + '\n**Responsable(s):** ' + owners +
                '\n**Entregable:** ' + task['deliverable'] +
                '\n\n[Plan y criterios de cierre](' + repo['url'] + '/blob/main/' + str(PLAN) +
                ')\n[Instrucciones de la tarea](' + repo['url'] + '/blob/main/' + ficha + ')')
        command = ['issue', 'create', '--title', '[' + task_id + '] ' + task['title'],
                   '--body', body, '--label', ','.join(labels_for(task_id, task)), '--milestone', task['phase']]
        for person in task['owners']:
            command.extend(['--assignee', users[person]])
        url = gh(*command)
        numbers[task_id] = url.rsplit('/', 1)[-1]
        task['body'] = body
        print(task_id + ' -> #' + numbers[task_id])
    for task_id, task in tasks.items():
        refs = ', '.join('#' + numbers[d] + ' (' + d + ')' for d in task['deps']) or 'nada'
        gh('issue', 'edit', numbers[task_id], '--body', task['body'] + '\n\n**Depende de:** ' + refs)
    print('Listo: ' + str(len(numbers)) + ' issues. Registrar la ejecución; no repetir el generador.')


try:
    main()
except (ValueError, RuntimeError, OSError) as exc:
    print('Error: ' + str(exc), file=sys.stderr)
    sys.exit(1)
PY
