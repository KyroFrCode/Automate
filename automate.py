# -*- coding: utf-8 -*-
from transition import *
from state import *
import os
import copy
from itertools import product
from automateBase import AutomateBase



class Automate(AutomateBase):
        
    def succElem(self, state, lettre):
        """State x str -> list[State]
        rend la liste des états accessibles à partir d'un état
        state par l'étiquette lettre
        """
        successeurs = []
        # t: Transitions
        for t in self.getListTransitionsFrom(state):
            if t.etiquette == lettre and t.stateDest not in successeurs:
                successeurs.append(t.stateDest)
        return successeurs


    def succ(self, listStates, lettre):
        """list[State] x str -> list[State]
        rend la liste des états accessibles à partir de la liste d'états
        listStates par l'étiquette lettre
        """
        #liste_etat: list[State]
        liste_etat = []

        #i: State
        for i in listStates:

            #j : State
            for j in self.succElem(i,lettre):
                liste_etat.append(j)
        
        return liste_etat



    """ Définition d'une fonction déterminant si un mot est accepté par un automate.
    Exemple :
            a=Automate.creationAutomate("monAutomate.txt")
            if Automate.accepte(a,"abc"):
                print "L'automate accepte le mot abc"
            else:
                print "L'automate n'accepte pas le mot abc"
    """
    @staticmethod
    def accepte(auto,mot) :
        """ Automate x str -> bool
        rend True si auto accepte mot, False sinon
        """
        #tmp: set(State)
        tmp = set(auto.getListInitialStates())
        #tmp2: set(State)
        tmp2 = set()
        #liste_finale : set(State)
        liste_finale = set(auto.getListFinalStates())

        #lettre : str
        for lettre in mot:
            
            tmp2.update(auto.succ(tmp,lettre))#parcours l'automate depuis etat initiale jusqu'a la dernière lettre du mot
            tmp = tmp2
            tmp2 = set()
            
        if(len(list(tmp.intersection(liste_finale)))>0): #verifie si le dernier etat transition est bien un etat final ou non
            print(f"le mot {mot} est accepte par l'automate")
            return True
            
        else:
            print(f"le mot {mot} n'est pas accepte par l'automate")
            return False


    @staticmethod
    def estComplet(auto,alphabet) :
        """ Automate x str -> bool
         rend True si auto est complet pour alphabet, False sinon
        """
        #lettre: str
        for lettre in alphabet:
            #state : State
            for state in auto.listStates:
            
                if(auto.succElem(state,lettre) == []): #verifie si chaque lettre a partir de l'etat a au moins un etat successeur
                
                    return False        
        
        return True


        
    @staticmethod
    def estDeterministe(auto) :
        """ Automate  -> bool
        rend True si auto est déterministe, False sinon
        """
        #lettre
        for lettre in auto.getAlphabetFromTransitions():
            #state : State
            for state in auto.listStates:
            
                if(len(auto.succElem(state,lettre)) != 1): #verifie si chaque lettre a partir de l'etat a au plus un etat successeur
                    
                    print("L'automate n'est pas deterministe")
                    return False
                            
        print("L'automate est deterministe")
        return True
        

       
    @staticmethod
    def completeAutomate(auto,alphabet) :
        """ Automate x str -> Automate
        rend l'automate complété d'auto, par rapport à alphabet
        """
        
        if(auto.estComplet(auto,alphabet)): #si il est complet on renvoie une copie de l'automate
            return copy.deepcopy(auto)
        
        else:

            #sp: State
            sp = State(1000,False,False,"⊥") #⊥ #création de l'etat puit
            autocomplete = copy.deepcopy(auto) #on copie l'automate

            #lettre: str
            for lettre in alphabet:

                autocomplete.addTransition(Transition(sp,lettre,sp))

                #state : State
                for state in auto.listStates:
                    if(len(auto.succElem(state,lettre)) == 0): #si il n'y a pas d'etat successeur on creer une transition vers l'etat puit
                        autocomplete.addTransition(Transition(state,lettre,sp))
                          
            return  autocomplete
       

    @staticmethod
    def determinisation(auto) :
        """ Automate  -> Automate
        rend l'automate déterminisé d'auto
        """
        if(auto.estDeterministe(auto)): #si l'automate est deterministe on renvoie une copie de l'automate
            return copy.deepcopy(auto)
            
        else:
            
            #alphabet: list[str]
            alphabet = auto.getAlphabetFromTransitions()
            #Liste_Transition: list[Transition]
            Liste_Transition = []
            #Liste_State: list[set(State)]
            Liste_State = [set(auto.getListInitialStates())]
            #tmp : list[set(State)]
            tmp = [set(auto.getListInitialStates())]
            
            while len(tmp) != 0: #on reste dans la boucle tant qu'on a pas traité tous les ensembles etats
                
                #s : set(State)
                for s in tmp:
                    tmp.remove(s)
                    #lettre: str
                    for lettre in alphabet:
                        #succ: set(State)
                        succ = set(auto.succ(s,lettre))

                        if succ not in Liste_State: #si l'ensemble d'etats successeur n'est pas dans Liste_State on le rajoute dans la liste et on le met dans tmp pour le traiter plus tard
                            Liste_State.append(succ)
                            tmp.append(succ)
                        
                        #init: bool
                        init = False #si tout les etats sont initiale il deviendra vrai 

                        #l1: str
                        l1 = "{"
                        for k in s:          #creer l'etiquette(label) de l'ensemble de l'etat s
                            l1+= k.label+","
                            init = init and k.init #verifie si tout les etats sont initiales ou non
                        l1 = l1[:(len(l1)-1)]+"}" #remplace le dernier "," par "}"

                        #etat1 : State
                        etat1= State(Liste_State.index(s),init,State.isFinalIn(s),l1)

                        #l2: str
                        l2 = "{"
                        for k in succ:
                            l2+= k.label+","
                        l2 = l2[:(len(l2)-1)]+"}"

                        #si le label est vide donc creation d'un nouveau etat contenant aucun etat donc ca devient un etat puit (ici juste remplace le label vide par le symbole du puit)
                        if(l2 =="}"):
                            l2 = "⊥" #⊥

                        #etat2: State
                        etat2= State(Liste_State.index(succ),False,State.isFinalIn(succ),l2)
                        
                        Liste_Transition.append(Transition(etat1,lettre,etat2))

            return Automate(Liste_Transition)
        
    @staticmethod
    def complementaire(auto,alphabet):
        """ Automate -> Automate
        rend  l'automate acceptant pour langage le complémentaire du langage de a
        """
        #Liste_States: list[State]
        Liste_States = []

        #auto_c: Automate
        auto_c = copy.deepcopy(auto)
        auto_c = Automate.determinisation(auto_c) #determinise l'automate si necessaire
        auto_c = Automate.completeAutomate(auto_c,alphabet) #complete l'automate si necessaire

        #etat: State
        for etat in auto_c.listStates:
            Liste_States.append(State(etat.id,etat.init,not etat.fin,etat.label)) #inverse l'etat final en non final et inversement

        return Automate(auto_c.listTransitions,Liste_States)

    @staticmethod
    def intersection (auto0, auto1):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """

        #Liste_Transition : list[Transition]
        Liste_Transition = []
        #Liste_States: list[(State x State)]
        Liste_States = list(product(auto0.listStates,auto1.listStates)) #fait le produit des etats auto0 et auto1
        #alphabet: str
        alphabet = auto0.getAlphabetFromTransitions()

        #lettre: str
        for lettre in alphabet:
            #e0,e1: Tuple[State]
            for e0,e1 in Liste_States:
                
                #State_Src: State
                State_Src = State(Liste_States.index((e0,e1)),(e0.init and e1.init),(e0.fin and e1.fin),"("+e0.label+","+e1.label+")")
                #etat_succ0,etat_succ1: Tuple[State]
                for etat_succ0,etat_succ1 in Liste_States:

                    if((Transition(e0,lettre,etat_succ0) in auto0.listTransitions) and (Transition(e1,lettre,etat_succ1) in auto1.listTransitions)): #si les transitions sont bien dans auto0 et auto1 on ajoute la transition dans la Liste_Transition apres la creation de l'etat Dest
                            
                            #State_dest: State
                            State_dest = State(Liste_States.index((etat_succ0,etat_succ1)),(etat_succ0.init and etat_succ1.init),(etat_succ0.fin and etat_succ1.fin),"("+etat_succ0.label+","+etat_succ1.label+")")
                            Liste_Transition.append(Transition(State_Src,lettre,State_dest))

        return  Automate(Liste_Transition)

    @staticmethod
    def union (auto0, auto1):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'union des langages des deux automates
        """
        #Liste_Transition: list[Transition]
        Liste_Transition = []

        if(len(set(auto0.listStates).intersection(auto1.listStates))==0): # si S1 n S2 = vide

            Liste_Transition = auto0.listTransitions + auto1.listTransitions
            return Automate(Liste_Transition)

        else:
            #Liste_States: list[(State x State)]
            Liste_States = list(product(auto0.listStates,auto1.listStates))
            #alphabet : str
            alphabet = auto0.getAlphabetFromTransitions()
            #lettre: str
            for lettre in alphabet:

                #e0,e1 : Tuple[State]
                for e0,e1 in Liste_States:
                    
                    #State_Src: State
                    State_Src = State(Liste_States.index((e0,e1)),(e0.init and e1.init),(e0.fin or e1.fin),"("+e0.label+","+e1.label+")")

                    #etat_succ0,etat_succ1: Tuple[State]
                    for etat_succ0,etat_succ1 in Liste_States:

                        if((Transition(e0,lettre,etat_succ0) in auto0.listTransitions) and (Transition(e1,lettre,etat_succ1) in auto1.listTransitions)): #si les transitions sont bien dans auto0 et dans auto1 alors on ajoute la transition dans  Liste_Transition
                            
                            #State_dest: State
                            State_dest = State(Liste_States.index((etat_succ0,etat_succ1)),(etat_succ0.init and etat_succ1.init),(etat_succ0.fin or etat_succ1.fin),"("+etat_succ0.label+","+etat_succ1.label+")")
                            Liste_Transition.append(Transition(State_Src,lettre,State_dest))

            return  Automate(Liste_Transition) 

   
       

    @staticmethod
    def concatenation (auto1, auto2):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage la concaténation des langages des deux automates
        """

        #Liste_Transition: list[Transition]
        Liste_Transition = []
        #S2_init: State
        S2_init = None #pour recuperer l'etat initiale de auto2
        #Initiale_Union: bool
        Initiale_Union = False #booleen pour savoir I = I1 ou (I1 et I2) [initiale state] pour A1=(S1,I1,F1,T1) et A2=(S2,I2,F2,T2)

        if(set(auto1.getListInitialStates()).intersection(auto1.getListFinalStates())): #si I1 n F1 != vide
            Initiale_Union = True

        #on traite auto2
        #t2: Transition
        for t2 in auto2.listTransitions:

            Liste_Transition.append(Transition(State(len(auto1.listStates)+t2.stateSrc.id,(Initiale_Union and t2.stateSrc.init),t2.stateSrc.fin,str(chr(64+t2.stateSrc.id))),t2.etiquette,State(len(auto1.listStates)+t2.stateDest.id,(Initiale_Union and t2.stateDest.init),t2.stateDest.fin,str(chr(64+t2.stateDest.id)))))
            if(t2.stateSrc.init):
                S2_init = t2.stateSrc

        #on traite auto1
        #t1: Transition
        for t1 in auto1.listTransitions:

            Liste_Transition.append(Transition(State(t1.stateSrc.id,t1.stateSrc.init,False,t1.stateSrc.label),t1.etiquette,State(t1.stateDest.id,t1.stateDest.init,False,t1.stateDest.label)))

            if(t1.stateDest.fin): #si on detect que stateDest est finale dans la transition t1 de auto1 alors on creer une transition etiquette de stateSrc vers S2_init
                Liste_Transition.append(Transition(State(t1.stateSrc.id,t1.stateSrc.init,False,t1.stateSrc.label),t1.etiquette,State(len(auto1.listStates)+S2_init.id,(Initiale_Union and S2_init.init),S2_init.fin,str(chr(64+S2_init.id)))))

        return Automate(Liste_Transition)
        
       
    @staticmethod
    def etoile (auto):
        """ Automate  -> Automate
        rend l'automate acceptant pour langage l'étoile du langage de a
        """

        #Liste_Transition : list[Transition]
        Liste_Transition = []

        #i_state: State
        for i_state in auto.getListInitialStates():
            
            #t: Transition
            for t in auto.listTransitions:

                if(t.stateSrc.init): #si l'etat est initiale on le transforme en etat finale (pour que epsilon soit accepter)

                    if(t.stateDest.init):
                        Liste_Transition.append(Transition(State(t.stateSrc.id,t.stateSrc.init,True,t.stateSrc.label),t.etiquette,State(t.stateDest.id,t.stateDest.init,True,t.stateDest.label)))
                    
                    else:
                        Liste_Transition.append(Transition(State(t.stateSrc.id,t.stateSrc.init,True,t.stateSrc.label),t.etiquette,t.stateDest))

                elif(t.stateDest.fin): #si l'etat de destination est finale alors on rajoute la transition t et une transition de l'etat source vers l'etat initiale dans Liste_Transition

                    Liste_Transition.append(t)
                    Liste_Transition.append(Transition(t.stateSrc,t.etiquette,State(i_state.id,i_state.init,True,i_state.label)))

                else: #sinon on rajoute le reste des transitions de l'automate
                    Liste_Transition.append(t)

        return Automate(Liste_Transition)    



