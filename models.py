from django.db import models

class Bitrix_zabbix(models.Model):
    problem_start = models.CharField(max_length=200, null=True)
    problem_name = models.CharField(max_length=200,null=True)
    host = models.CharField(max_length=200,null=True)
    severity = models.CharField(max_length=200,null=True)
    problem_id = models.CharField(max_length=200,null=True)
    

    def __str__(self):
        return self.problem_name




class Host_zabbix(models.Model):
    host = models.CharField(max_length=100, null=True)
    host_name = models.CharField(max_length=200, null=True)
    

    def __str__(self):
        return self.host_name







