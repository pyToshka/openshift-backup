# Backup databases for Openshift/Kunbernetes

Backup script for databases in OpenShift Container Platform v3 or Kubernetes

### Dependencies

```
Python >= 2.7
openshift==0.7.2
kubernetes==7.0.0
urllib3==1.23

```

### Instalation

```bash
git clone https://github.com/pyToshka/openshift-backup.git
cd openshift-backup
cp config_example.ini config.ini
pip install -r requirements.txt
python ./backup_db.py
```

Add user token to config file

### Labeling
The label "backup" needs to be set inside the deploymentconfig at the jsonpath '.spec.template.metadata.labels'.

example:

```yaml
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: php-app
        backup: mysql
        service: php-db

```

### Available tags

| Tag name  |Value   |  Description |
|---|---|---|
|backup   | mysql  | backup mysql databases  |
| backup  | postgresql  |  backup postgresql databases |
