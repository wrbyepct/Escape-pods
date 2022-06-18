-------------------------------- MODULE EP3 --------------------------------
EXTENDS Integers, Sequences, TLC, FiniteSets, Naturals
CONSTANTS IntermediateProviders, Quota, SupplyRecords, Requesters
VARIABLES sr, quota, AC, target, requesters, total
    

(***************************************************************************)
(*   Variable defs:                                                        *)
(*     1. sr = Supply Records                                              *)
(*     2. quota = Quota                                                    *)
(*     3. AC = Asking Chain                                                *)
(*     4. target = Currently focused target                                *)
(*     5. requesters = Exit Rooms                                          *)
(*     6. total = the list numbers that every requester can get            *)
(***************************************************************************)
vars == <<sr, quota, AC, target, requesters, total>>
\* Check for valid suppliers, quota has to be greater than 0 & not in the asker chain
GetDPs(a, chain) == SelectSeq(IntermediateProviders, LAMBDA p: (quota[p][a] > 0) /\ (p \notin chain) ) 

GetStatus(p, akr, a_asked, a_chain) == [   name |-> p,          
                                            DSA |-> IF sr[p] >= a_asked THEN a_asked ELSE sr[p],                
                                       cur_hold |-> IF sr[p] >= a_asked THEN a_asked ELSE sr[p], 
                                            DPs |-> GetDPs(p, a_chain),
                                            akr |-> akr,
                                      requested |-> a_asked,
                                          chain |-> {p} \cup a_chain  ]
                               
\* Making sure ask no more than the quota
AskAmount(pdr, akr, asked) ==   
                 IF quota[pdr][akr] =< asked 
               THEN quota[pdr][akr]
               ELSE asked
GetRequesterDP == GetStatus(requesters[1], -1, 10000, {-1})

               
GetIP == GetStatus(
                    target.DPs[1], 
                LET t == [target EXCEPT!["DPs"] = Tail(target["DPs"])]                                                              
                 IN t, 
                    AskAmount(target.DPs[1], target.name, target.requested),
                    target.chain   )
   
   
             
               
               
\* Update supply recodrds as soon as the new DP is created               
UpdateSR(Ip, IpHold) == sr' = [sr EXCEPT![Ip] = sr[Ip] - IpHold]   
  
\* Update the quota after the cur_hold is given             
UpdateQuota(p, a, p_hold) ==  quota' = [quota EXCEPT![p][a] = quota[p][a] - p_hold] 

GiveAndUpdateQuota ==         
         /\ target' = [target EXCEPT !["akr"]["cur_hold"] = target["akr"]["cur_hold"] + target["cur_hold"],
                                     !["cur_hold"] = 0,
                                     !["requested"] = target["requested"] - target["cur_hold"]]  
         /\ UpdateQuota(target.name, target["akr"].name, target["cur_hold"])
         
CheckQuota == quota[target.name][target["akr"].name]          

                                   
(***************************************************************************)
(* Condition 1: If target has nothing to give                              *)
(* Condiiton 2: and quota for its asker is 0 or it has no one to ask       *)
(* Actions:                                                                *)
(*   1. Make switch the target to the previous one                         *)
(*   2. Remove the last one in AC                                          *)
(*   3. Update the second last one                                         *)
(***************************************************************************)                                   
                                   
CanRemove == 
          /\ target["cur_hold"] = 0
          /\ \/ CheckQuota = 0
             \/ target["DPs"] = <<>> 
           

\* Remove the last one in AC and update the the second last one
Remove == 
       /\ CanRemove
       /\ AC' = [i \in 1..(Len(AC)-1) |-> IF i = (Len(AC)-1) THEN target["akr"] ELSE AC[i]]
       /\ target' = target["akr"]  
       /\ UNCHANGED <<requesters, sr, quota, total>>

(***************************************************************************)
(* Condition 1: If now target is not exit room                             *)
(* Condition 2: Quota from target to its asker is not 0                    *)
(* Condition 3: Target still have some DPs                                 *)
(* Condition 4: Target has noting to give                                  *)
(* Actions:                                                                *)
(*   1. Add the new IP to AC                                               *)
(*   2. Update supply records                                              *)
(***************************************************************************)

AddIPAndSwitchT ==  
        /\  AC' = LET IP == GetIP
                  IN Append(AC, IP) \* Add IP to AC
        /\ target' = AC'[Len(AC')]  \* switch target
        /\ UpdateSR(target'.name, target'.DSA)

CanAskDP == 
        /\ target["cur_hold"] = 0
        /\ CheckQuota > 0
        /\ target["DPs"] # <<>>
        /\ AddIPAndSwitchT      
        /\ UNCHANGED <<quota, requesters, total>>
       

(***************************************************************************)
(* Condition 1: target's current hold is greater than 0                    *)
(* Actions:                                                                *)
(*   1. Update asker and quota                                             *)
(*   2. Clear target's hold                                                *)
(*   3. No change for these variables                                      *)
(***************************************************************************)

CanGiveAkr == 
            /\ target["cur_hold"] > 0
            /\ GiveAndUpdateQuota         
            /\ UNCHANGED <<sr, AC, requesters, total>>


(***************************************************************************)
(*  Condition 1: And it has no DP left(target["DPs"] = <<>>)               *)
(*  Actions:                                                               *)
(*     1. Give the its cur_hold to total list                              *)                                                                  
(*     2. Remove it from AC                                                *)
(*     3. No change for these variables(sr, quota, requesters)             *)
(*                                                                         *)
(***************************************************************************)
UpdateTotal ==
           /\ target["DPs"] = <<>>
           /\ total' = Append(total, target["cur_hold"])
           /\ AC' = Tail(AC)
           /\ UNCHANGED <<sr, quota, requesters, target>>


(***************************************************************************)
(* Condition 1: There's still some DP to ask                               *)
(* Actions:                                                                *)
(*    1. Create an IP from the first DP of taret                           *)
(*    2. Append it to AC                                                   *)
(*    3. Remove the first DP from the target's DP                          *)
(*    4. No change for these variables(sr, quota, total)                   *)
(***************************************************************************)
RequesterAddIP ==
           /\ target["DPs"] # <<>>
           /\ AddIPAndSwitchT 
           /\ UNCHANGED <<quota, total, requesters>> 

(***************************************************************************)
(* Condition 1: If there's no IP in AC                                     *)
(* Condition 2: IF there's still requesters in the List(requester # << >>) *)
(* Actions:                                                                *)
(*  1. Select the first requester and create an IP                         *)
(*  2. Add the IP to AC                                                    *)
(*  3. Change the target to the AC's first IP                              *)
(*  4. Remove the first one in requesters(requesters' = Tail(requesters))  *)
(*  5. No change to sr, quota, target, total                               *)
(***************************************************************************)      
SelectRequesterAndAddToAC ==             
                /\  requesters # <<>>
                /\         AC' = LET DP == GetRequesterDP
                                  IN Append(AC, DP)
                /\ target' = AC'[1]                              
                /\ requesters' = Tail(requesters)     
                /\ UNCHANGED <<sr, quota, total>>                

                    
Init == 
      /\         sr = SupplyRecords
      /\      quota = Quota     
      /\     target = GetStatus(1, -1, 10000, {-1})
      /\ requesters = Requesters  
      /\         AC = <<target>>
      /\      total = <<>>


Next == 
  \/ /\ Len(AC) = 0
     /\ SelectRequesterAndAddToAC \* Has nothing in AC, pick one in requesters and remove it from requesters 
  \/ /\ Len(AC) = 1
     /\ \/ RequesterAddIP \* When AC only has requester, and it have DPs to ask, add one to AC 
        \/ UpdateTotal \* When the requester has nothing to ask, append its hold to total list, and remove itself                  
  \/ /\ Len(AC) > 1     
     /\ \/ CanGiveAkr \* Once have something to give and has quota, give  
        \/ CanAskDP \* Havs nothing to give, and still has quota, and still has DPs
        \/ Remove \* Has nothing above, remove and switch target

  
SUM == LET Sum[ i \in 1..Len(total) ] == IF i = 1 THEN total[i] ELSE total[i] + Sum[i-1]
        IN IF total = <<>> THEN 0 ELSE Sum[Len(total)]   
Expectation == <>[](SUM = 160)
Spec == Init /\ [][Next]_vars

FairSpec == Spec /\ WF_vars(Next)     

THEOREM FairSpec => Expectation          
=============================================================================
\* Modification History
\* Last modified Sat Jun 18 21:42:47 CST 2022 by wrbyepct
\* Created Thu Jun 16 23:15:36 CST 2022 by wrbyepct
