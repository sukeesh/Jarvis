import click
try:
    from .core import *
except:
    from core import *
    
@click.command()
@click.option('--mode','-m',default="meaning",help="Mode of Script [meaning, antonym, synonym]")
@click.option('--words', '-w',prompt="Enter words in a string separated by commas")
def script(words,mode):
    print("PyDictionary:")
    word_values = [w.strip() for w in words.split(',')]
    d = PyDictionary(word_values)
    maps = {"meaning":d.printMeanings,"antonym":d.printAntonyms,"synonym":d.printSynonyms}
    click.echo(maps[mode]())
