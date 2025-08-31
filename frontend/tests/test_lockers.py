from django.test import TestCase
from lockers.models import Locker, Lock


class LockerModelTest(TestCase):
    def setUp(self):
        self.locker = Locker.objects.create(name="LockerA", location="Warszawa")
        self.lock_small_free = Lock.objects.create(locker=self.locker, size="small", is_free=True)
        self.lock_large_occupied = Lock.objects.create(locker=self.locker, size="large", is_free=False)

    def test_str_method_locker(self):
        self.assertEqual(str(self.locker), "Automat: LockerA adres: Warszawa")

    def test_get_free_locks(self):
        free_locks = self.locker.get_free_locks()
        self.assertIn(self.lock_small_free, free_locks)
        self.assertNotIn(self.lock_large_occupied, free_locks)

    def test_cascade_delete_locker_deletes_locks(self):
        locker_id = self.locker.id
        self.locker.delete()
        self.assertFalse(Lock.objects.filter(locker_id=locker_id).exists())


class LockModelTest(TestCase):
    def setUp(self):
        self.locker = Locker.objects.create(name="LockerB", location="Białystok")
        self.lock = Lock.objects.create(locker=self.locker, size="small", is_free=True)

    def test_str_method_lock_free(self):
        self.assertEqual(str(self.lock), f"Lock in {self.locker.name} (small) - Wolna")

    def test_str_method_lock_occupied(self):
        self.lock.is_free = False
        self.lock.save()
        self.assertEqual(str(self.lock), f"Lock in {self.locker.name} (small) - Zajęta")
