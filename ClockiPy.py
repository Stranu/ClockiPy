#  TODO: Multithreading per la gestione delle finestre con liste (non aggiornabili in maniera dinamica)
#  Impostazione orari di lavoro per l'auto "stoppaggio" e salvataggio dei task quando si attiva la checkbox

import sys
import PySimpleGUI as sg
import time
import datetime
import csv
import os

PATH = "csv"
USER = "/user.csv"
USERHEADER = ["ID", "Username", "Theme"]
TASK = "/tasks.csv"
TASKHEADER = ["TaskID", "UserID", "ProgettoID", "NomeTask", "Inizio", "Fine", "Attivo"]
INTERVALLI = "/intervals.csv"
INTERVALLIHEADER = ["UserID", "Fine"]
PROGETTI = "/projects.csv"
PROGETTIHEADER = ["UserID", "NomeProgetto"]
EXPORT = "sal.csv"
EXPORTHEADER = ["Progetto", "Task", "Data inizio", "Data fine", "Durata (Ore, minuti, secondi)"]
LOGSPEGNIMENTO = "/logspegnimento.csv"
LOGHEADER = ["TaskAttivoID", "Time"]


def storeData(filename, entry, mode='a'):
    if not os.path.isfile(filename):
        mode = 'w'
    with open(filename, mode, newline='') as csvfile:
        content = csv.writer(csvfile, delimiter=';', quotechar='|')
        content.writerow(entry)


def updateData(filename, entry, id):
    oldfile = retrieve(filename)
    storeData(filename, header(filename), "w")
    for elements in oldfile:
        if int(elements[0]) == id:
            if entry:
                storeData(filename, entry)
        else:
            storeData(filename, elements)


def header(filename):
    """return the first row of the csv as a list"""
    if os.path.isfile(filename):
        with open(filename, newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='|')
            header = next(content)
            return header
    else:
        print(f'\n!Il file -{filename}- non esiste!')
        return []


def retrieve(filename):
    if os.path.isfile(filename):
        temp_list = []
        with open(filename, newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='|')
            next(content)
            for row in content:
                temp_list.append(row)

            return temp_list
    else:
        print(f'\n!Il file -{filename}- non esiste!')
        return []


def retrieveBigger(filename, position):  # Return the biggest value in that column (might be the ID, starting time
    # etc..)
    oldfile = retrieve(filename)
    current = 0
    if oldfile:
        for elements in oldfile:
            if int(elements[position]) > current:
                current = int(elements[position])
        return current
    else:
        return 0


def retrieveLast(filename):
    oldfile = retrieve(filename)
    lastElement = []
    if oldfile:
        for elements in oldfile:
            lastElement = elements
        return lastElement
    else:
        return []


def isActive():
    tasks = retrieve(PATH + TASK)
    for elements in tasks:
        if elements[6] == "True":
            return elements
    return False


def retrieveByX(haystack, needle,
                position):  # haystack is a list of lists, needle the element to look for, position is the where
    hayFound = [hay for hay in haystack if hay[position] == needle]
    if hayFound:
        return hayFound[0]
    else:
        return False


def intervalToStringOraMinSec(number):
    temp = number // 100
    hours = temp // 3600
    temp = temp - 3600 * hours
    minutes = temp // 60
    seconds = temp - 60 * minutes
    return '{:02d}:{:02d}.{:02d}'.format(hours, minutes, seconds)


# __________________________ Check folder and file existence_________________________
if not os.path.exists(PATH):
    os.makedirs(PATH)
if not os.path.isfile(PATH + USER):
    storeData(PATH + USER, USERHEADER)
    layoutUser = [[sg.Text('Benvenuto su ClockiPy, dimmi come ti chiami (Cognome e nome)')],
                  [sg.Text('->: '), sg.InputText(key='Username')],
                  [sg.Button('Salva', key='Salva'), sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]]
    windowLogin = sg.Window('ClockiPy', layoutUser, auto_size_buttons=True, keep_on_top=True,
                            grab_anywhere=True)
    while True:
        event, values = windowLogin.read()
        if event is None or event == 'Exit':  # ALWAYS give a way out of program
            windowLogin.Close()
            break
        if event == 'Salva':
            userID = 1
            storeData(PATH + USER, [userID, values['Username'], "Reddit"])
            windowLogin.Close()
            break

try:
    user = retrieve(PATH + USER)
except:
    quit()
userID = user[0][0]

if not os.path.isfile(PATH + TASK):
    storeData(PATH + TASK, TASKHEADER)
if not os.path.isfile(PATH + INTERVALLI):
    storeData(PATH + INTERVALLI, INTERVALLIHEADER)
    storeData(PATH + INTERVALLI, [userID, "13:00:00, 18:00:00"])
if not os.path.isfile(PATH + PROGETTI):
    storeData(PATH + PROGETTI, PROGETTIHEADER)
if not os.path.isfile(PATH + LOGSPEGNIMENTO):
    storeData(PATH + LOGSPEGNIMENTO, LOGHEADER)
projects = retrieve(PATH + PROGETTI)  # Check if there is atleast one project. If not, force the creation of one
if not projects:
    layoutProject = [
        [sg.Text('Devi inserire almeno un nome di un progetto. In futuro potrai modificarlo o aggiungerne altri.')],
        [sg.Text('->: '), sg.InputText(key='Project')],
        [sg.Button('Salva', key='Salva'), sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]]
    windowProject = sg.Window('ClockiPy', layoutProject, auto_size_buttons=True, keep_on_top=True,
                              grab_anywhere=True)
    while True:
        event, values = windowProject.read()
        if event is None or event == 'Exit':  # ALWAYS give a way out of program
            windowProject.Close()
            break
        if event == 'Salva':
            projectID = 1
            storeData(PATH + PROGETTI, [projectID, values['Project']])
            windowProject.Close()
            break
try:
    projectsList = retrieve(PATH + PROGETTI)
except:
    quit()
projectID = projectsList[-1][0]

# ----------------  Create Form  ----------------
#  sg.ChangeLookAndFeel('Reddit')
sg.ChangeLookAndFeel(user[0][2])
sg.SetOptions(element_padding=(0, 0))

"""menu_def = [['File', ['Show Tasks List', 'Export', 'Exit']],
            ['Edit', ['Change Theme'], ],
            ['Help', 'About...'], ]"""
menu_def = [['File', ['Export', 'Exit']],
            ['Edit', ['Change Theme'], ],
            ['Help', 'About...'], ]
projNameList = [proj[1] for proj in projectsList]
intervals = retrieve(PATH + INTERVALLI)
intervals = [interv.strip() for interv in intervals[0][1].split(",")]
"""layout = [[sg.Menu(menu_def, )],
          [sg.Text('Nome Task: '), sg.InputText(key="Task")],
          [sg.Text('00:00.00', size=(12, 2), font=('Helvetica', 20), justification='center', key='text')],
          [sg.Text("Progetto attuale: "), sg.Combo(projNameList, key='comboProject')],
          [sg.Button('Avvia', key='runStop', button_color=('white', '#001480')),
           sg.Exit(button_color=('white', 'firebrick4'), key='Exit')],
          [sg.Text(size=(40, 2), key='logTask')],
          [sg.Text('')],
          [sg.Text('')],
          [sg.Text('')],
          [sg.Text('Aggiungi un progetto: '), sg.InputText(key="newProject")],
          [sg.Button('Aggiungi', key='addProject', button_color=('white', 'gray'))],
          [sg.Text('')],
          [sg.Text('')]]"""
layout = [[sg.Menu(menu_def, )],
          [sg.Text('Nome Task: '), sg.InputText(key="Task")],
          [sg.Button('+', key="Edit", tooltip="Modifica l'orario di inizio del task"),
           sg.Text('00:00.00', size=(12, 1), font=('Helvetica', 20), key='text')],
          [sg.Text("Progetto attuale: "), sg.Text(key='comboProject', size=(40, 1)),
           sg.Button('Scegli', key='chooseProject', button_color=('white', 'gray'), tooltip="Scegli, modifica, "
                                                                                            "elimina o aggiungi un "
                                                                                            "nuovo progetto da "
                                                                                            "abbinare al task")],
          [sg.Button('Avvia', key='runStop', button_color=('white', '#001480')),
           sg.Exit(button_color=('white', 'firebrick4'), key='Exit')],
          [sg.Text(size=(40, 2), key='logTask')],
          [sg.Text('')],
          [sg.Text('')],
          [sg.Button("Widget", key="Widget", tooltip="Riduci tutto ad un widget più discreto. Rimarrà sempre visibile "
                                                     "sullo schermo"),
           sg.Text(' ', size=(18, 1), key='textFarlocco'),
           sg.Checkbox("Usa intervalli di lavoro", key="intervalliSiNo", tooltip="Impostando degli orari di lavoro, "
                                                                                 "si potrà dire a clockiPy di "
                                                                                 "interrompere il task rispettando "
                                                                                 "gli orari scelti"),
           sg.Combo(intervals, key='combointervals', default_value=intervals[-1]),
           sg.Button("Modifica", key="modificaIntervalli")]]

window = sg.Window('ClockiPy', layout, auto_size_buttons=True, keep_on_top=False)

# ----------------  main loop  ----------------
current_time = 0
paused = True
justStarted = True
start_time = int(round(time.time() * 100))
paused_time = start_time
layoutProjectArray = []
windowProjectArray = []

#  check if there is a task still active to recover
activeTask = isActive()
if activeTask:
    paused = False
    taskID = int(activeTask[0])

while True:
    # --------- Read and update window --------
    if not paused:
        intervals = retrieve(PATH + INTERVALLI)
        event, values = window.read(timeout=10)
        current_time = int(round(time.time() * 100)) - start_time
        if values and values["intervalliSiNo"]:
            actualTime = datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y')
            intervalsNum = int(time.mktime(time.strptime(actualTime + " " + values["combointervals"], "%d-%m-%Y %H:%M:%S")))
            if intervalsNum * 100 <= int(round(time.time() * 100)):
                layoutIntervalAlarm = [
                    [sg.Text(f"Sono le ore {values['combointervals']}! Si è attivato l'intervallo di lavoro da te "
                             f"impostato\n "
                             f"Interrompo e salvo il Task usando questo orario come riferiemento? [Salva] o "
                             f"vuoi riprenderne l'esecuzione? [Riprendi]")],
                    [sg.Button("Ferma e Salva", key="fermaESalva"), sg.Button("Riprendi", key="riprendi")]]
                windowIntervalAlarm = sg.Window("Riprendi?", layoutIntervalAlarm, keep_on_top=True)
                while True:
                    eventTask, valuesTask = windowIntervalAlarm.read()
                    if eventTask is None or eventTask == 'riprendi':
                        window["intervalliSiNo"].update(False)
                        windowIntervalAlarm.Close()
                        break
                    elif eventTask == "fermaESalva":
                        activeTask[5] = intervalsNum * 100
                        activeTask[6] = False
                        updateData(PATH + TASK, activeTask, int(activeTask[0]))
                        activeTask = []
                        paused = True
                        windowIntervalAlarm.Close()
                        break
    else:
        event, values = window.read()
    if event == 'runStop':
        event = window[event].GetText()

    if activeTask and justStarted:  # If there's a task with "Active" set to True, start from there
        logSpegnimento = retrieve(PATH + LOGSPEGNIMENTO)
        logSpegnimento = logSpegnimento[-1]
        if logSpegnimento[0] == activeTask[0]:
            dataSpegniemnto = datetime.datetime.fromtimestamp(float(logSpegnimento[1]) / 100).strftime(
                '%d-%m-%Y %H:%M:%S')
            layoutRipresaTask = [[sg.Text(f"Il programma è stato chiuso in questa data: {dataSpegniemnto} mentre il "
                                          f"task {activeTask[3]} era in esecuzione\n"
                                          f"Interrompo e salvo il Task usando quella data come riferiemento? [Salva] o "
                                          f"vuoi riprenderne l'esecuzione? [Riprendi]")],
                                 [sg.Button("Ferma e Salva", key="fermaESalva"), sg.Button("Riprendi", key="riprendi")]]
            windowRipresaTask = sg.Window("Riprendi?", layoutRipresaTask, keep_on_top=True)
            while True:
                eventTask, valuesTask = windowRipresaTask.read()
                if eventTask is None or eventTask == 'riprendi':
                    start_time = int(round(float(activeTask[4])))
                    projectID = activeTask[2]
                    currentProject = retrieveByX(projectsList, projectID, 0)
                    paused_time = start_time
                    window['logTask'].update(f'Stai eseguendo il task {activeTask[3]}')
                    window['runStop'].update(text='Stop&Save')
                    window['Task'].update(value=activeTask[3])
                    window['comboProject'].update(value=currentProject[1])
                    windowRipresaTask.Close()
                    break
                elif eventTask == "fermaESalva":
                    activeTask[5] = logSpegnimento[1]
                    activeTask[6] = False
                    updateData(PATH + TASK, activeTask, int(activeTask[0]))
                    activeTask = []
                    paused = True
                    windowRipresaTask.Close()
                    break
        justStarted = False

    # --------- Do Button Operations --------
    if event is None or event == 'Exit':  # ALWAYS give a way out of program
        activeTask = isActive()
        if activeTask:
            storeData(PATH + LOGSPEGNIMENTO, [activeTask[0], int(round(time.time() * 100))])
        break
    """if event == 'Reset':
        start_time = int(round(time.time() * 100))
        current_time = 0
        paused_time = start_time"""
    if event == 'Stop&Save':
        paused = True
        paused_time = int(round(time.time() * 100))
        wrongformat = False
        layoutEdit = [[sg.Text("Vuoi interrompere e salvare il Task? (puoi modificare l'orario prima di confermare)")],
                      [sg.InputText(
                          datetime.datetime.fromtimestamp(float(paused_time) / 100).strftime('%d-%m-%Y %H:%M:%S'),
                          key="editableTime")],
                      [sg.Button("Conferma", key="modifica"), sg.Exit()]]
        windowEdit = sg.Window("Edit Time", layoutEdit, grab_anywhere=False)
        while True:
            eventEdit, valuesEdit = windowEdit.read()
            if eventEdit is None or eventEdit == 'Exit':  # ALWAYS give a way out of program
                windowEdit.Close()
                break
            if eventEdit == "modifica":
                activeTask = isActive()
                if activeTask:
                    endTime = valuesEdit["editableTime"]
                    try:
                        endTimeNum = int(time.mktime(time.strptime(endTime, "%d-%m-%Y %H:%M:%S"))) * 100
                    except:
                        wrongformat = True
                    if endTime == "" or wrongformat:
                        sg.PopupOK("Non hai scelto date valide o hai usato un formato errato!")
                    elif endTimeNum < start_time:
                        sg.PopupOK("La data di fine del task non può essere precedente alla data di inizio")
                    else:
                        paused_time = endTimeNum
                        element = window['runStop']
                        element.update(text='Avvia')
                        window['logTask'].update(f'Hai stoppato il task {values["Task"]}')
                        updateData(PATH + TASK,
                                   [taskID, userID, projectID, values["Task"], start_time, paused_time, False], taskID)
                        start_time = int(round(time.time() * 100))
                        paused_time = start_time
                        windowEdit.Close()
                        break
                else:
                    sg.PopupOK("Non c'è nessun task attivo al momento."
                               "di inizio")
                    windowEdit.Close()
                    break
    elif event == 'Avvia':
        paused = False
        start_time = start_time + int(round(time.time() * 100)) - paused_time
        element = window['runStop']
        element.update(text='Stop&Save')
        window['logTask'].update(f'Stai eseguendo il task {values["Task"]}')
        taskID = retrieveBigger(PATH + TASK, 0)
        taskID += 1
        # Inserisce nel CSV una nuova riga creando un ID più i vari campi
        storeData(PATH + TASK, [taskID, userID, projectID, values["Task"], start_time, "", True])
    elif event == 'addProject':  # TEST
        newProjName = values['newProject']
        newProjID = retrieveBigger(PATH + PROGETTI, 0)
        newProjID += 1
        yesNo = sg.PopupYesNo('Sei sicuro di voler creare il progetto ' + newProjName + "?")
        if yesNo == "Yes":
            storeData(PATH + PROGETTI, [newProjID, newProjName])
            projNameList.append(newProjName)
            print(projNameList)
            window['comboProject'].update("hh", "lll", "fjfjf")
    elif event == "chooseProject":
        layoutChooseProject = [
            [sg.Radio("", "radio1", key=proj[0], background_color="gray",
                      default=True if int(proj[0]) == int(projectID) else False),
             sg.InputText(proj[1], key="name_" + proj[0])]
            for proj in projectsList]
        layoutChooseProject.append(
            [sg.Radio("", "radio1", key="nuovoProj", background_color="gray"), sg.InputText(key="newProjName")])
        layoutChooseProject.append([sg.Text()])
        layoutChooseProject.append([sg.Button("Scegli/Modifica/Aggiungi", key="Scegli"),
                                    sg.Button("Elimina", key="Elimina", button_color=('white', 'firebrick4')),
                                    sg.Exit(button_color=('white', 'firebrick4'))])
        layoutProjectArray.append(layoutChooseProject)
        windowChooseProject = sg.Window('Projects', layoutProjectArray[len(layoutProjectArray) - 1])
        while True:
            eventProj, valuesProj = windowChooseProject.read()
            if eventProj is None or eventProj == 'Exit':  # ALWAYS give a way out of program
                windowChooseProject.Close()
                break
            if eventProj == "Scegli" or eventProj == "Elimina":
                for proj in projectsList:
                    if valuesProj[proj[0]]:
                        newChoosenName = valuesProj["name_" + proj[0]]
                        if eventProj == "Elimina":
                            #  TODO: Se non coincide col progetto in uso, non cambiare il nome ed il valore attuale
                            updateData(PATH + PROGETTI, [], int(proj[0]))
                            if projectID == int(proj[0]):
                                projectID = 1
                                newChoosenName = retrieve(PATH + PROGETTI)
                                newChoosenName = newChoosenName[0][0]
                                window["comboProject"].update(value=newChoosenName)
                            sg.PopupOK("Progetto eliminato correttamente.\n"
                                       "Per vedere le modifiche in questa lista, sarà necessario chiudere e riaprire "
                                       "il programma")
                        elif eventProj == "Scegli":
                            updateData(PATH + PROGETTI, [proj[0], newChoosenName], int(proj[0]))
                            projectID = proj[0]
                            window["comboProject"].update(value=newChoosenName)
                            sg.PopupOK("Progetto scelto correttamente.\n")
                        currentTask = isActive()
                        if currentTask:
                            updateData(PATH + TASK,
                                       [currentTask[0], currentTask[1], projectID, currentTask[3], currentTask[4],
                                        currentTask[5], currentTask[6]], int(currentTask[0]))
                        windowChooseProject.Close()
                        break
                #  Se non fa parte dei progetti esistenti, vacreato uno nuovo
                if valuesProj["nuovoProj"]:
                    newProjID = retrieveBigger(PATH + PROGETTI, 0)
                    newProjID += 1
                    projectID = newProjID
                    if valuesProj["newProjName"]:
                        storeData(PATH + PROGETTI, [newProjID, valuesProj["newProjName"]])
                        window["comboProject"].update(value=valuesProj["newProjName"])
                        currentTask = isActive()
                        if currentTask:
                            updateData(PATH + TASK,
                                       [currentTask[0], currentTask[1], projectID, currentTask[3], currentTask[4],
                                        currentTask[5], currentTask[6]], int(currentTask[0]))
                        sg.PopupOK("Progetto assegnato e creato correttamente.\n"
                                   "Per poterlo visualizzare in questa lista, sarà necessario chiudere e riaprire il "
                                   "programma")
                        windowProjectArray[-1].Close()
                        break
                    else:
                        sg.PopupOK("Devi inserire un nome prima")
    elif event == 'Edit':
        wrongformat = False
        layoutEdit = [[sg.InputText(
            datetime.datetime.fromtimestamp(float(start_time) / 100).strftime('%d-%m-%Y %H:%M:%S'),
            key="editableTime")],
            [sg.Button("Modifica", key="modifica"), sg.Exit()]]
        windowEdit = sg.Window("Edit Time", layoutEdit, grab_anywhere=False)
        while True:
            eventEdit, valuesEdit = windowEdit.read()
            if eventEdit is None or eventEdit == 'Exit':  # ALWAYS give a way out of program
                windowEdit.Close()
                break
            if eventEdit == "modifica":
                activeTask = isActive()
                if activeTask:
                    newStart = valuesEdit["editableTime"]
                    try:
                        newStartNum = int(time.mktime(time.strptime(newStart, "%d-%m-%Y %H:%M:%S"))) * 100
                    except:
                        wrongformat = True
                    if newStart == "" or wrongformat:
                        sg.PopupOK("Non hai scelto date valide o hai usato un formato errato!")
                    elif newStartNum > int(round(time.time() * 100)):
                        sg.PopupOK("La data di inizio del task non più venire dal futuro")
                    else:
                        # TODO: modificare nel file task.csv la data di inizio del task corrispondente (se nessun task è
                        #  stato avviato, segnalarlo)
                        activeTask[4] = newStartNum
                        updateData(PATH + TASK, activeTask, int(activeTask[0]))
                        start_time = newStartNum
                        sg.PopupOK("Data ed ora di inizio modificata correttamente")
                        windowEdit.Close()
                        break
                else:
                    sg.PopupOK("Non c'è nessun task attivo al momento. Questa funzione serve per modificarne l'orario "
                               "di inizio")
                    windowEdit.Close()
                    break
    elif event == 'modificaIntervalli':
        oldIntervals = retrieve(PATH + INTERVALLI)
        textIntervals = ""
        if oldIntervals:
            oldIntervals = oldIntervals[0]
            textIntervals = oldIntervals[1]
        layouIntervals = [[sg.Text("Indica gli orari di fine lavoro\n(seguendo il formato hh:mm:ss, separati da una "
                                   "virgola)")],
                          [sg.Multiline(default_text=textIntervals, size=(43, 5), key="intervalli")],
                          [sg.Button("Salva", key="salva"), sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]]
        windowIntervals = sg.Window('Intervals', layouIntervals, keep_on_top=False)
        while True:
            eventIntervals, valuesIntervals = windowIntervals.read()
            if eventIntervals is None or eventIntervals == 'Exit':  # ALWAYS give a way out of program
                windowIntervals.Close()
                break
            elif eventIntervals == "salva":
                intervalliNew = valuesIntervals["intervalli"]
                intervalliNew = intervalliNew.strip()
                intervalli = intervalliNew.split(",")
                wrongformat = False
                # time.mktime(time.strptime(dataSceltaInizio, "%d-%m-%Y %H:%M:%S"))
                for intervallo in intervalli:
                    try:
                        checkIntervallo = time.strptime(intervallo.strip(), "%H:%M:%S")
                    except:
                        wrongformat = True
                if not intervallo or wrongformat:
                    sg.PopupOK("Non hai scelto orari validi o hai usato un formato errato!")
                else:
                    if oldIntervals:
                        oldIntervals[1] = intervalliNew
                        updateData(PATH + INTERVALLI, oldIntervals, int(oldIntervals[0]))
                    else:
                        storeData(PATH + INTERVALLI, [1, intervalliNew])
                    window["combointervals"].update(values=intervalli)
                    window["combointervals"].update(intervalli[-1])
                    sg.PopupOK("Intervalli salvati correttamente")
                    windowIntervals.Close()
                    break
    elif event == 'Show Tasks List':
        layoutList = [[sg.Exit(button_color=('white', 'firebrick4'), key='Exit')], [sg.Text("Esempio")]]
        for x in range(5):
            layoutList.append([sg.Text(f"Esempio {x}")])
        windowList = sg.Window('List', layoutList, auto_size_buttons=False, keep_on_top=False,
                               grab_anywhere=True)
        while True:
            event, values = windowList.read()
            if event is None or event == 'Exit':  # ALWAYS give a way out of program
                windowList.Close()
                break
        # TODO: Da completare CANCELLA e AGGIUNGI
    elif event == "Widget":
        layoutWidget = [[sg.Text(values["Task"], key="TaskW", size=(20, 1))],
                        [sg.Text('00:00.00', size=(12, 1), font=('Helvetica', 12),
                                 key='textW')],
                        [sg.Button('Main Page', key='main', button_color=('white', '#001480'))]]
        windowWidget = sg.Window("Widget ClockiPy", layoutWidget, grab_anywhere=True, keep_on_top=True,
                                 no_titlebar=True)
        window.Hide()
        while True:
            if not paused:
                eventW, valuesW = windowWidget.read(timeout=10)
                current_time = int(round(time.time() * 100)) - start_time
            else:
                eventW, valuesW = windowWidget.read()
            if eventW is None or eventW == 'main':  # ALWAYS give a way out of program
                windowWidget.Close()
                window.UnHide()
                break
            current_time_str = intervalToStringOraMinSec(current_time)
            windowWidget['textW'].update(current_time_str)
    elif event == "Export":
        # EXPORT = "sal.csv"
        # EXPORTHEADER = ["Progetto", "Task", "Data inizio", "Data fine", "Durata"]
        #  userName = user[0][1].replace(" ", "_")
        freeToGo = True
        filename = False
        dataSceltaInizio = ""
        dataSceltaFine = ""
        dataSceltaInizioNum = 0
        dataSceltaFineNum = 0
        wrongformat = False
        layoutPeriod = [[sg.Text("Scegli un intervallo di tempo: (gg/mm/aaaa)")],
                        [sg.CalendarButton("Dal...", key="inizio", close_when_date_chosen=True,
                                           target="dataInizio", format='%d-%m-%Y')],
                        [sg.InputText(key="dataInizio")],
                        [sg.CalendarButton("...al", key="fine", close_when_date_chosen=True,
                                           target="dataFine", format='%d-%m-%Y')],
                        [sg.InputText(key="dataFine")],
                        [sg.Button("Continua"), sg.Exit()]]
        windowPeriod = sg.Window("Period", layoutPeriod, auto_size_buttons=False, keep_on_top=False,
                                 grab_anywhere=True)
        while True:
            event, values = windowPeriod.read()
            if event is None or event == 'Exit':  # ALWAYS give a way out of program
                windowPeriod.Close()
                freeToGo = False
                break
            if event == "Continua":
                dataSceltaInizio = values["dataInizio"] + " 00:00:00"
                dataSceltaFine = values["dataFine"] + " 23:59:59"
                try:
                    dataSceltaInizioNum = time.mktime(time.strptime(dataSceltaInizio, "%d-%m-%Y %H:%M:%S"))
                    dataSceltaFineNum = time.mktime(time.strptime(dataSceltaFine, "%d-%m-%Y %H:%M:%S"))
                except:
                    wrongformat = True
                if dataSceltaInizio == "" or dataSceltaFine == "" or wrongformat:
                    sg.PopupOK("Non hai scelto date valide o hai usato un formato errato!")
                elif dataSceltaFineNum < dataSceltaInizioNum:
                    sg.PopupOK("La data finale non può essere più piccola della data iniziale")
                else:
                    windowPeriod.Close()
                    break
        while freeToGo:
            filename = sg.PopupGetFile(f'Scegli dove esportare il file (Scegliere come estensione il .csv)\n'
                                       f'Dal {dataSceltaInizio} al {dataSceltaFine}',
                                       default_extension=".csv", save_as=True, file_types=(('CSV', '.csv'),))
            if not filename:
                break
            elif ".csv" in filename:
                break
            else:
                filename = filename.split(".")
                filename = filename[0] + ".csv"
                break
        if filename:
            # filename = userName + "_" + EXPORT
            oldTask = retrieve(PATH + TASK)
            totaleTempo = 0
            if oldTask:
                storeData(filename, EXPORTHEADER, "w")
                taskInInterval = [task for task in oldTask if
                                  dataSceltaInizioNum <= (float(task[4])) / 100 <= dataSceltaFineNum and task[
                                      6] == "False"]
                for task in taskInInterval:
                    if task[6] == "False":
                        dataInizio = datetime.datetime.fromtimestamp(float(task[4]) / 100).strftime('%d-%m-%Y %H:%M:%S')
                        dataFine = datetime.datetime.fromtimestamp(float(task[5]) / 100).strftime('%d-%m-%Y %H:%M:%S')
                        durata = int(task[5]) - int(task[4])
                        totaleTempo += durata
                        durataStr = intervalToStringOraMinSec(durata)
                        userName = user[0][1].replace(" ", "_")
                        associaProject = retrieveByX(projectsList, task[2], 0)
                        storeData(filename, [associaProject[1], task[3], dataInizio, dataFine, durataStr])
                totaleStr = intervalToStringOraMinSec(totaleTempo)
                storeData(filename, ["", "", "", "Totale (Ore:min:sec):", totaleStr])
                sg.PopupOK('File esportato con successo')
            else:
                sg.PopupOK("Non ci sono elementi da esportare nell'intervallo di tempo scelto")
    elif event == "Change Theme":
        layoutThemes = [[sg.Text('Tema attuale: '), sg.Text(user[0][2], key="temaAttuale")],
                        [sg.Text("Seleziona una delle voci per avere an'ateprima del tema")],
                        [sg.Listbox(values=sg.theme_list(),
                                    size=(20, 12), key='-LIST-', enable_events=True)],
                        [sg.Button("Salva", key="imposta"), sg.Button("Ripristina default", key="default"),
                         sg.Button('Exit')]]

        windowThemes = sg.Window('Look and Feel Browser', layoutThemes)

        while True:  # Event Loop
            eventThemes, valuesThemes = windowThemes.read()
            if eventThemes in (None, 'Exit'):
                break
            elif eventThemes == "imposta":
                user[0][2] = valuesThemes['-LIST-'][0]
                updateData(PATH + USER, user[0], int(userID))
                windowThemes["temaAttuale"].update(valuesThemes['-LIST-'][0])
                sg.PopupOK("Tema impostato correttamente. Per rendere efettiva la modifica sarà necessario riavviare "
                           "CloickiPy")
            elif eventThemes == "default":
                user[0][2] = "Reddit"
                updateData(PATH + USER, user[0], int(userID))
                windowThemes["temaAttuale"].update("Reddit")
                sg.PopupOK("Tema resettato. Per rendere efettiva la modifica sarà necessario riavviare "
                           "CloickiPy")
            else:
                sg.theme(valuesThemes['-LIST-'][0])
                sg.popup_get_text('This is {}'.format(valuesThemes['-LIST-'][0]))

        windowThemes.close()

    # --------- Display timer in window --------
    # window['text'].update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
    #                                                    (current_time // 100) % 60,
    #                                                    current_time % 100))
    #  window['text'].update('{:02d}:{:02d}.{:02d}'.format(hours, minutes, seconds))
    current_time_str = intervalToStringOraMinSec(current_time)
    window['text'].update(current_time_str)
    # window['text'].update(datetime.datetime.fromtimestamp(float(current_time)/100).strftime('%H:%M:%S'))
