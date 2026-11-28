"""python -m atolye [--acma]   (--acma: tarayıcıyı açma)"""
import sys

from .sunucu import calistir

calistir(ac="--acma" not in sys.argv)
