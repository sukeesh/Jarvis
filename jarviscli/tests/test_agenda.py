import unittest
#from jarviscli.CmdInterpreter import JarvisAPI
from tests import PluginTest  
import datetime
from plugins.write_agenda import write_agenda
#from plugins.write_agenda import read_agenda

class WriteAgendaTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(write_agenda)

    def test_write_agenda_date(self):
        eventDate = "2022-02-02"
        temp= datetime.datetime.strptime(eventDate, '%Y-%m-%d')
        self.queue_input(eventDate)
        self.queue_input(temp)
        
        #self.queue_input("")
        #self.queue_input("")
        self.test.run(self.jarvis_api)
        
        self.assertEqual(self.history_say().last_text(), 'Write down the event date (ex. 2021-09-21):')
        
    def test_write_agenda_all(self):
        eventDate = "2022-02-02"
        temp= datetime.datetime.strptime(eventDate, '%Y-%m-%d')
        self.queue_input(eventDate)
        self.queue_input(temp)
        self.test.run(self.jarvis_api)
        
        d= self.test(self.jarvis_api,"")
        self.assertEqual(d, 'Write down the event date (ex. 2021-09-21):')
        
        self.queue_input('Write down the event time (ex. 13:00):')
        
        self.test.run('2022-02-02')
        self.assertIn('2022-02-02',self.history_say().view_text())
        self.queue_input('Write down the event place:')
        self.queue_input('Write down the event title:')
        self.queue_input('Write down the event description:')
        self.queue_input('Would you like to add anything more?():')
        d = self.test.write_agenda(self.jarvis_api)
        
        #d= self.test(self.jarvis_api,self)
        self.assertEqual(d, 'Write down the event date (ex. 2021-09-21):')
        self.assertEqual(d, 'Write down the event time (ex. 13:00):')
        self.assertEqual(d, 'Write down the event place:')
        self.assertEqual(d, 'Write down the event title:')
        self.assertEqual(d, 'Write down the event description:')
        self.assertEqual(d, 'Would you like to add anything more?(y/n):')



if __name__ == '__main__':
    unittest.main()
