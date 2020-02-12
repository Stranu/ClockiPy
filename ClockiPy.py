import sys
import PySimpleGUI as sg
import time
import datetime
import csv
import os

PATH = "csv"
USER = "/user.csv"
USERHEADER = ["ID", "Username"]
TASK = "/tasks.csv"
TASKHEADER = ["TaskID", "UserID", "ProgettoID", "NomeTask", "Inizio", "Fine", "Attivo"]
INTERVALLI = "/intervals.csv"
INTERVALLIHEADER = ["UserID", "Inizio", "Fine"]
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
    windowLogin = sg.Window('ClockiPy', layoutUser, auto_size_buttons=False, keep_on_top=True,
                            grab_anywhere=True)
    while True:
        event, values = windowLogin.read()
        if event is None or event == 'Exit':  # ALWAYS give a way out of program
            windowLogin.Close()
            break
        if event == 'Salva':
            userID = 1
            storeData(PATH + USER, [userID, values['Username']])
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
    windowProject = sg.Window('ClockiPy', layoutProject, auto_size_buttons=False, keep_on_top=True,
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
sg.ChangeLookAndFeel('Reddit')
sg.SetOptions(element_padding=(0, 0))

"""menu_def = [['File', ['Show Tasks List', 'Export', 'Exit']],
            ['Edit', ['Change Theme'], ],
            ['Help', 'About...'], ]"""
menu_def = [['File', ['Export', 'Exit']],
            ['Edit', ['Change Theme (WIP)'], ],
            ['Help', 'About...'], ]
projNameList = [proj[1] for proj in projectsList]
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
          [sg.Text('00:00.00', size=(12, 2), font=('Helvetica', 20), justification='center', key='text')],
          [sg.Text("Progetto attuale: "), sg.Text(key='comboProject', size=(40, 1)),
           sg.Button('Scegli', key='chooseProject', button_color=('white', 'gray'))],
          [sg.Button('Avvia', key='runStop', button_color=('white', '#001480')),
           sg.Exit(button_color=('white', 'firebrick4'), key='Exit')],
          [sg.Text(size=(40, 2), key='logTask')],
          [sg.Text('')],
          [sg.Text('')],
          [sg.Button("Widget", key="Widget")]]

window = sg.Window('ClockiPy', layout, auto_size_buttons=False, keep_on_top=False)

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
        event, values = window.read(timeout=10)
        current_time = int(round(time.time() * 100)) - start_time
    else:
        event, values = window.read()
    if event == 'runStop':
        event = window[event].GetText()

    if activeTask and justStarted:  # If there's a task with "Active" set to True, start from there
        logSpegnimento = retrieve(PATH + LOGSPEGNIMENTO)
        logSpegnimento = logSpegnimento[-1]
        if logSpegnimento[0] == activeTask[0]:
            dataSpegniemnto = datetime.datetime.fromtimestamp(float(logSpegnimento[1]) / 100).strftime('%d-%m-%Y %H:%M:%S')
            yesNo = sg.PopupYesNo(f"Il programma è stato chiuso in questa data: {dataSpegniemnto} mentre il task "
                                  f"{activeTask[3]} era in esecuzione\n"
                                  f"Interrompo e salvo il Task usando quella data come riferiemnto? [Yes] o vuoi "
                                  f"riprenderne l'esecuzione? [No]")
            if yesNo == "Yes":
                activeTask[5] = logSpegnimento[1]
                activeTask[6] = False
                updateData(PATH + TASK, activeTask, int(activeTask[0]))
                activeTask = []
                paused = True
            else:
                start_time = int(round(float(activeTask[4])))
                projectID = activeTask[2]
                currentProject = retrieveByX(projectsList, projectID, 0)
                paused_time = start_time
                window['logTask'].update(f'Stai eseguendo il task {activeTask[3]}')
                window['runStop'].update(text='Stop&Save')
                window['Task'].update(value=activeTask[3])
                window['comboProject'].update(value=currentProject[1])
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
        element = window['runStop']
        element.update(text='Avvia')
        window['logTask'].update(f'Hai stoppato il task {values["Task"]}')
        # TODO: Modifica nel CSV inserendo FINE e mettendo a False ATTIVO
        updateData(PATH + TASK, [taskID, userID, projectID, values["Task"], start_time, paused_time, False], taskID)
        start_time = int(round(time.time() * 100))
        paused_time = start_time
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
    elif event == 'addProject':
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
        #  layoutProjectArray = []
        layoutChooseProject = [
            [sg.Radio("", "radio1", key=proj[0], background_color="gray",
                      default=True if int(proj[0]) == int(projectID) else False), sg.InputText(proj[1], key="name_" + proj[0])]
            for proj in projectsList]
        layoutChooseProject.append(
            [sg.Radio("", "radio1", key="nuovoProj", background_color="gray"), sg.InputText(key="newProjName")])
        layoutChooseProject.append([sg.Text()])
        layoutChooseProject.append([sg.Button("Scegli/Modifica/Aggiungi", key="Scegli"),
                                    sg.Button("Elimina", key="Elimina", button_color=('white', 'firebrick4')),
                                    sg.Exit(button_color=('white', 'firebrick4'))])
        layoutProjectArray.append(layoutChooseProject)
        #  windowChooseProject = sg.Window('Projects', layoutProjectArray[len(layoutProjectArray)-1])
        windowProjectArray.append(sg.Window('Projects', layoutProjectArray[-1]))
        while True:
            eventProj, valuesProj = windowProjectArray[-1].read()
            if eventProj is None or eventProj == 'Exit':  # ALWAYS give a way out of program
                windowProjectArray[-1].Close()
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
                        windowProjectArray[-1].Close()
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
                        [sg.Text('00:00.00', size=(12, 1), font=('Helvetica', 12), justification='center',
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
                dataSceltaInizio = values["dataInizio"]
                dataSceltaFine = values["dataFine"]
                try:
                    dataSceltaInizioNum = time.mktime(time.strptime(dataSceltaInizio, "%d-%m-%Y"))
                    dataSceltaFineNum = time.mktime(time.strptime(dataSceltaFine, "%d-%m-%Y"))
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
        print("TODO: elements == Change Theme")
        listaTemi = ['Black', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'Dark', 'Dark2', 'DarkAmber',
                     'DarkBlack', 'DarkBlack1', 'DarkBlue', 'DarkBlue1', 'DarkBlue10', 'DarkBlue11', 'DarkBlue12',
                     'DarkBlue13', 'DarkBlue14', 'DarkBlue15', 'DarkBlue16', 'DarkBlue17', 'DarkBlue2', 'DarkBlue3',
                     'DarkBlue4', 'DarkBlue5', 'DarkBlue6', 'DarkBlue7', 'DarkBlue8', 'DarkBlue9', 'DarkBrown',
                     'DarkBrown1', 'DarkBrown2', 'DarkBrown3', 'DarkBrown4', 'DarkBrown5', 'DarkBrown6',
                     'DarkGreen', 'DarkGreen1', 'DarkGreen2', 'DarkGreen3', 'DarkGreen4', 'DarkGreen5',
                     'DarkGreen6', 'DarkGrey', 'DarkGrey1', 'DarkGrey2', 'DarkGrey3', 'DarkGrey4', 'DarkGrey5',
                     'DarkGrey6', 'DarkGrey7', 'DarkPurple', 'DarkPurple1', 'DarkPurple2', 'DarkPurple3',
                     'DarkPurple4', 'DarkPurple5', 'DarkPurple6', 'DarkRed', 'DarkRed1', 'DarkRed2', 'DarkTanBlue',
                     'DarkTeal', 'DarkTeal1', 'DarkTeal10', 'DarkTeal11', 'DarkTeal12', 'DarkTeal2', 'DarkTeal3',
                     'DarkTeal4', 'DarkTeal5', 'DarkTeal6', 'DarkTeal7', 'DarkTeal8', 'DarkTeal9', 'Default',
                     'Default1', 'DefaultNoMoreNagging', 'Green', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak',
                     'LightBlue', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4', 'LightBlue5',
                     'LightBlue6', 'LightBlue7', 'LightBrown', 'LightBrown1', 'LightBrown10', 'LightBrown11',
                     'LightBrown12', 'LightBrown13', 'LightBrown2', 'LightBrown3', 'LightBrown4', 'LightBrown5',
                     'LightBrown6', 'LightBrown7', 'LightBrown8', 'LightBrown9', 'LightGray1', 'LightGreen',
                     'LightGreen1', 'LightGreen10', 'LightGreen2', 'LightGreen3', 'LightGreen4', 'LightGreen5',
                     'LightGreen6', 'LightGreen7', 'LightGreen8', 'LightGreen9', 'LightGrey', 'LightGrey1',
                     'LightGrey2', 'LightGrey3', 'LightGrey4', 'LightGrey5', 'LightGrey6', 'LightPurple',
                     'LightTeal', 'LightYellow', 'Material1', 'Material2', 'NeutralBlue', 'Purple', 'Reddit',
                     'Reds', 'SandyBeach', 'SystemDefault', 'SystemDefault1', 'SystemDefaultForReal', 'Tan',
                     'TanBlue', 'TealMono', 'Topanga']
        layoutTheme = [[sg.Combo(listaTemi, key="sceltaTemi")],
                       [sg.Button("Imposta Tema", key="imposta"), sg.Exit()]]
        windowTheme = sg.Window("Scelta Tema", layoutTheme)
        while True:
            eventT, valuesT = windowTheme.read()
            if eventT is None or eventT == 'Exit':  # ALWAYS give a way out of program
                windowTheme.Close()
                break
            elif eventT == "imposta":
                print(valuesT["sceltaTemi"])
                sg.ChangeLookAndFeel(valuesT["sceltaTemi"])

    # --------- Display timer in window --------
    # window['text'].update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
    #                                                    (current_time // 100) % 60,
    #                                                    current_time % 100))
    #  window['text'].update('{:02d}:{:02d}.{:02d}'.format(hours, minutes, seconds))
    current_time_str = intervalToStringOraMinSec(current_time)
    window['text'].update(current_time_str)
    # window['text'].update(datetime.datetime.fromtimestamp(float(current_time)/100).strftime('%H:%M:%S'))
