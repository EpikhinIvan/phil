from django.db import models

class UserRequest(models.Model):
    user_id = models.IntegerField(verbose_name='Юзер')  
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
   
    report_category = models.CharField(max_length=255, verbose_name='Категория')
    report_text = models.TextField(verbose_name='Описание')
    location_lat = models.FloatField(verbose_name='латитуд', blank=True, null=True)
    location_lon = models.FloatField(verbose_name='лонг', blank=True, null=True)
    time = models.DateTimeField(verbose_name='Время создания', auto_now_add=True)
    report_photo= models.ImageField(upload_to='report_photos/', verbose_name='Фотография')
    status = models.BooleanField(default= True, verbose_name='Статус')

    class Meta:
        verbose_name = "Запрос пользователя"
        verbose_name_plural = "Запросы пользователей"
    
    def __str__(self):
        return f'Заявка {self.user_id}'


class AdminResponse(models.Model):
    user_request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, verbose_name='Заявка')
    admin_full_name = models.CharField(max_length=255 ,verbose_name='ФИО')
    admin_response_text = models.TextField(verbose_name='Описание')
    admin_response_photo = models.ImageField(upload_to='response_photos/', verbose_name='Фотография')
    response_time = models.DateTimeField(auto_now_add=True, verbose_name='Время ответа')

    class Meta:
        verbose_name = "Ответ админа"
        verbose_name_plural = "Ответы админов"
