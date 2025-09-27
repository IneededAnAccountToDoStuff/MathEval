r'''The Definitive* Order Of Operations

RTL=Right-To-Left

(,) 0 Parenthesis : Isolates part of the expression to be locally pre-computed before being evaluated by the rest of the expression
 |  0 Absolute Value Bars : Similar to parentheses, returns the absolute value of the inner expression, sometimes ambiguous as to what is in/out of it. Because of the ambiguity, it is not allowed in the math parser.
 ^  1 Exponents : RTL
()root()/√ 0 Roots : as it defines captures by parentheses
|> ·/*/x 2 Multiplication
|-1	: Implicit Multiplication → muddy waters…
|> \/ 2 Division

|> + 3 Addition
|-1
|> - 3 Subtraction


*! 1.4 Factorial - just above negation
func() 0 Functions(Parenthetical) = direct modification of parenthetical value
+ 1.5 plus = RTL, same as negation except it does nothing
- 1.5 negation = RTL, just below exponents
mod|% 1.6 Modulo
% 1.4 Percent

A complication with unary operators appears in cases such as "a^-b" and "a!^b". In both cases, the exponent has the higher precedence, but the given unary operators are unambiguous, since there is on'y a single direction for them to bind in.
'''

r'''
Wednesday, July 24, 2024 9:38 AM = 2024/7/24 09:38:38 (Unix: 1721831918797)
Beginning of changelog. State 1.
Changes made 2024/7/24:
    fixing factorial non-float issues, auto-convert if valid.
    adding processor settings
    adding multi-factorial as a process option
    adding implicit multiplication heuristic as a process option
    added braces as fractional cut
    removed tex parser from this file - belongs in separate project.
Changes 2024/8/24:
    factorial is now using non-naïve computation.
Changes 2025/9/23:
    Parser complete overhaul from scratch.
Changes 2025/9/24:
    New from scratch evaluator for the new parser from yesterday.
    Overhauled everything else to work with the new parser+evaluator.
    Parser has added AST optimisation feature & toggle (default:off)
    2 Major Parser Bugs found(^+ & multifactorial), one fixed
Changes 2025/9/25:
    Turns out the one fixed yesterday wasn't. Today I fixed the multifactorial system. Improved the __main__ interpreter. Also fixed the other bug.
    Added if? and switch?
    Added optimisations to AST optimiser
Changes 2025/9/26:
    Added support for operation calling (f+g)(a)
    Combined functions list and constants list for above support
    Extended ^ unary attachment to general a^--b case.
    Improved optimiser by getting it to work with the new ^ system, and optimising cases "-a/-b" , `¬(a{comparsion}b)`
'''

def tokenise(text:str,plusbraces={'[]':-1,'{}':-1},_log=False):
    'Tokenises the text into an AST that can be evaluated. _log controls if the program logs output data. Plusbraces is explained in the parserdoc variable'
    optimisationflag=not not plusbraces.get('--optimise',0)
    _log(f'||START:: {text}')if _log else None
    brackets:tuple[tuple[str,None|str],...]=(('()',None),('⌊⌋','+floor+'),('⌈⌉','+ceil+'))
    if plusbraces.get('[]',-1)!=-1:brackets=(*brackets,('[]',plusbraces['[]']))
    if plusbraces.get('{}',-1)!=-1:brackets=(*brackets,('{}',plusbraces['{}']))
    operators:list[tuple[int,dict[str,str],tuple[int,...]]|tuple[int,dict[str,str],tuple[int,...],tuple[int,...]]]=[(-1,({'**':'^','^':'^'},(1,-1))),(1,({'%':'percent','!':'!','‰':'permille','‱':'permyriad'},(-1,),(1,))),(1,({'‼':'‼'},(1,-1))),(1,({'+':'pos','-':'neg'},(1,),(-1,))),(1,({'!':'derange','¬':'¬'},(1,),(-1,))),(1,({'⋅':'*','*':'*','/':'/','÷':'/','mod':'mod','%':'mod'},(1,-1))),(1,({'+':'+','-':'-'},(1,-1))),(1,({'≥':'≥','>=':'≥','≤':'≤','<=':'≤','≠':'≠','!=':'≠','==':'=','=':'=','>':'>','<':'<'},(1,-1)))]
    #brackstart=[i[0][0]for i in brackets];brackends={i[0][0]:i[0][1]for i in brackets};brackfunc={i[0][1]:i[1]for i in brackets}
    brackstart=['(','⌊','⌈'];brackends={'(':')','⌊':'⌋','⌈':'⌉'};brackfunc={')':None,'⌋':'+floor+','⌉':'+ceil+'}
    #NOTE: should brackstart & sepchar_ be a set?
    #sepchar_=[i for j,_ in brackets for i in j];r_oper={*(j for _,(i,*_)in operators for j in i),','};funcbreakers={*r_oper,*(j for i,_ in brackets for j in i)}
    sepchar_=['(',')','⌊','⌋','⌈','⌉'];
    r_oper={'-','¬','<','÷','+','≥','>','=','==','!=','*','≠','!','<=','‼','⋅','^','mod','>=','/','%','**',',','≤','‰','‱'};funcbreakers={'-','¬','<','÷','‼','⋅','⌈','(','^','mod','⌉','+','>=','≥','>','/',')','=','%','==','**','⌋',',','!=','*','≠','⌊','!','<=','≤','‰','‱'}
    #unaries=[(b,c[0]==(1,))for _,(b,*c)in operators if 2==len(c)];unaries=({a:b for i,v in unaries if v for a,b in i.items()},{a:b for i,v in unaries if not v for a,b in i.items()})
    unaries=({'+':'pos','-':'neg','!':'derange','¬':'¬'},{'%':'percent','!':'!','‰':'permille','‱':'permyriad'})
    #Zero Pass: gluing
    text=text.replace('\n','').replace('\t','').replace(' ','').replace('‼','!!');spinach=[];ind=0;buff:list[str]=[]
    _log('Pre-Pass')if _log else None
    while ind<len(text):
        char=text[ind];possiblematches=[i for i in r_oper if i[0]==char]
        _log(f'\t{char=} {possiblematches=} {spinach=}')if _log else None
        if possiblematches:
            possiblematches.sort(key=len,reverse=True);flag=0
            for pos in possiblematches:
                if text[ind:ind+len(pos)]==pos:flag=1;spinach.append(''.join(buff));buff.clear();spinach.append(pos);ind+=len(pos);break
            if flag:continue
        if char in sepchar_:ind+=1;spinach.append(''.join(buff));spinach.append(char);buff.clear()
        else:ind+=1;buff.append(char)
    spinach.append(''.join(buff));spinach=[i for i in spinach if i]
    _log(f'Post-Pre-Pass: {spinach}')if _log else None
    stack:list[list[int,int,int,None|str]]=[[0,0,0,None]]#stack format: const start, const end, recurse search, const func
    while stack:
        brackbalance=0;kick=0;finalind=len(spinach);matchbrac=None;nextrec=None;startind,endind,searchpoint,funcval=currow=stack[-1];_log(f'Cur Iteration: {startind}-{endind} : {spinach[startind:finalind-endind]}\nFull Stack: {stack}\nCur State: {spinach}\nRecscan: {searchpoint} : {spinach[searchpoint:finalind-endind]}\nF-Val: {funcval=}')if _log else None;endind=finalind-endind
        #Bracket detection pass
        while 1:
            _log('\tView Element:')if _log else None
            if searchpoint==finalind:_log('\tEOD')if _log else None;break
            elif searchpoint==endind:_log('\tEOS')if _log else None;break
            element=spinach[searchpoint];_log(f'\t{element}')if _log else None
            if matchbrac and element==matchbrac[1]:
                if brackbalance==0:
                    spinach.pop(searchpoint);fw=brackfunc[element];start,val=nextrec
                    if fw is not None and val is not None:raise SyntaxError('Non-parenthetical bracket cannot use a function')
                    val=(None if fw is None else fw)if val is None else val;_log(f'\tElement bracket end, type {fw}. Recurse')if _log else None;stack.append([start,finalind-searchpoint-2,start,val]);kick=1;break
                else:brackbalance-=1
            elif matchbrac and element==matchbrac[0]:brackbalance+=1
            elif not matchbrac and element in brackstart:
                _log('\tElement bracket start')if _log else None
                vv=None
                if searchpoint:
                    tt=spinach[searchpoint-1]
                    if tt not in funcbreakers:searchpoint-=1;spinach.pop(searchpoint);vv=tt;_log(f'\tCaptured Function {tt}')if _log else None
                currow[2]=searchpoint;spinach.pop(searchpoint);nextrec=searchpoint,vv;brackbalance=0;matchbrac=(element,brackends[element]);continue
            searchpoint+=1
        if kick:continue
        stack.pop()
        #Operations pass
        _log(f'Betwixt: {startind} {endind} {spinach[startind:endind]} {spinach=}')if _log else None
        for dir,(ops,*bc)in operators:
            bca,bcd=bc if 2==len(bc)else(bc[0],None)
            if{'‼':'‼'}==ops:continue
            _log(f'\tOperator: {dir} {ops} {bca} {bcd}')if _log else None;opq=[i for i in ops if i in spinach[startind:endind]]
            if not opq:_log('Skip cycle')if _log else None;continue
            while 1:
                looper=range(startind,endind)if dir==1 else range(endind-1,startind-1,-1);_log(f'{looper=} {startind=} {endind=}')if _log else None
                for index in looper:
                    if spinach[index]in ops:
                        #NOTE: The '^'== and '!'==ops[oper] fixes for cases such as a%^!b. In applies to all binary operators, but ^ is the only one with high enough precedence to matter, so optimisation means only checking for it.
                        oper=spinach[index];f=1
                        if'^'==ops[oper]:
                            oper=spinach[index];f=1;fc=1;UN=unaries[0]
                            while 1:
                                if not index+fc<len(spinach):f=0;break
                                v=spinach[index+fc]
                                if v in r_oper and not v in UN:f=0;break
                                if not isinstance(v,str)or v not in UN:break
                                fc+=1
                            if f and fc>1:
                                tpr=spinach[fc+index];endind-=fc-1
                                for i in spinach[fc+index-1:index:-1]:
                                    tpr=(UN[i],tpr)
                                    if optimisationflag:
                                        qc=tpr[0]
                                        if'pos'==qc:tpr=tpr[1]
                                        elif'neg'==qc:
                                            if'neg'==tpr[1][0]:tpr=tpr[1][1]
                                            elif'0'==tpr[1]:tpr='0'
                                        elif'¬'==qc:
                                            if'¬'==tpr[1][0]and tpr[1][1][0]=='¬':tpr=tpr[1][1]
                                            if'='==tpr[1][0]:tpr=('≠',*tpr[1][1:])
                                            elif'≠'==tpr[1][0]:tpr=('=',*tpr[1][1:])
                                            elif'>'==tpr[1][0]:tpr=('≤',*tpr[1][1:])
                                            elif'<'==tpr[1][0]:tpr=('≥',*tpr[1][1:])
                                            elif'≤'==tpr[1][0]:tpr=('>',*tpr[1][1:])
                                            elif'≥'==tpr[1][0]:tpr=('<',*tpr[1][1:])
                                spinach[index+1:fc+index+1]=(tpr,)
                            if f:
                                fc=1;UN=unaries[1]
                                while 1:
                                    if not 0<=index-fc:f=0;break
                                    v=spinach[index-fc]
                                    if v in r_oper and not v in UN:f=0;break
                                    if not isinstance(v,str)or v not in UN:break
                                    fc+=1
                                if f and fc>1:
                                    tpr=spinach[index-fc]
                                    multifacr=0
                                    for i in spinach[index-fc+1:index]:
                                        if'!'==i:multifacr+=1
                                        else:
                                            if multifacr:tpr=('!',tpr)if multifacr==1 else('‼',tpr,f'{multifacr}');multifacr=0
                                            tpr=(UN[i],tpr)
                                    if multifacr:tpr=('!',tpr)if multifacr==1 else('‼',tpr,f'{multifacr}')
                                    spinach[index-fc:index]=(tpr,);endind-=fc-1;index-=fc-1
                            if f:
                                find=spinach.pop(index+1);newind=index-1;endind-=2;opchar=ops[oper];res=(opchar,spinach.pop(index-1),find)
                                if optimisationflag:
                                    if'1'==find:res=res[1]
                                    elif('neg','1')==find:res=('/','1',res[1])
                                spinach[newind]=res;_log(f'FLAG! ^ {index=} {newind=} {spinach=}')if _log else None;break
                        elif oper=='!'==ops[oper]:
                            offset=0
                            while index+offset<endind and'!'==spinach[index+offset]:offset+=1
                            assert(-1,)==bca and(1,)==bcd;A=index-1;lenspinach=len(spinach)
                            if(not 0<=A<lenspinach)or(isinstance(spinach[A],str)and spinach[A]in r_oper):print(f'\tMissing at relative -1 mapped to {A} for !')if _log else None;f=0
                            if f and bcd is not None:
                                D=index+offset
                                if 0<=D<lenspinach and(not isinstance(spinach[D],str)or spinach[D]not in r_oper):print(f'\tExcessive at relative 1 mapped to {D} for !')if _log else None;f=0
                            if f:
                                einds=spinach.pop(index-1);newind=index-1;endind-=offset
                                if offset==1:spinach[newind]=('!',einds)
                                else:spinach[newind:newind+offset]=[('‼',einds,f'{offset}')];_log(f'FLAG‼ {oper=} {einds=} {inds=} {index=} {newind=} {spinach=}')if _log else None
                                break
                                #TODO: ‼ get integers working with evaltokens
                        else:
                            oper=spinach[index];f=1;inds=[]
                            for a in bca:
                                if(not 0<=index+a<len(spinach))or(isinstance(spinach[index+a],str)and spinach[index+a]in r_oper):f=0;break
                                inds.append(a)
                            if f and bcd is not None:
                                for d in bcd:
                                    if 0<=index+d<len(spinach)and(not isinstance(spinach[index+d],str)or spinach[index+d]not in r_oper):f=0;break
                            if f:
                                finds=sorted((spinach.pop(index+i)for i in inds if i>0));einds=sorted((spinach.pop(index+i)for i in inds if i<0),reverse=True);ll=len(einds);newind=index-ll;endind-=ll+len(finds);opchar=ops[oper];res=(opchar,*einds,*finds)
                                if optimisationflag:
                                    #These were rejected for certain (usually 0) holes in the correctness   ('-',('+',n,a),a) → n | ('-',('+',n,a),n) → a | ('+',n,('-',a,a)) → n | ('+',n,('-',a,n)) → a | ('=',a,a) → True | ('≥',a,a) → True | ('≤',a,a) → True | ('≠',a,a) → False | ('<',a,a) → False | ('>',a,a) → False | ('-',a,a) → 0 | ('^',1,a) → 1 | ('^',0,a) → 0 | ('^',a,0) → 1 | ('mod',0,n) → 0  ||  I also chose not to implement special numeric optimisations, aside from specific cases. General number-number optimisations are considered user side problems 'number-number=0 | number/number=1 if number else 0/0 | 0/number=0 if number else 0/0'
                                    if'+'==opchar:
                                        tmp=(*(i for i in(*(einds[0][1:]if'+'==einds[0][0][0]else einds),*(finds[0][1:]if'+'==finds[0][0][0]else finds))if'0'!=i),)
                                        if len(tmp)>2:res=('+n',*tmp)
                                        elif len(tmp)==0:res='0'
                                        elif len(tmp)==1:res=tmp[0]
                                        elif'neg'==tmp[1][0]:res=('-',tmp[0],tmp[1][1])
                                        elif'neg'==tmp[0][0]:res=('-',tmp[1],tmp[0][1])
                                        else:res=('+',*tmp)
                                    elif'*'==opchar:
                                        tmp=(*(einds[0][1:]if'*'==einds[0][0][0]else einds),*(finds[0][1:]if'*'==finds[0][0][0]else finds));count=sum(1 for i in tmp if'neg'==i[0])%2;tmp=(*(i for i in(i[1]if'neg'==i[0]else i for i in tmp)if'1'!=i),)
                                        #if any(i=='0'for i in tmp):res=('0')# optimisation dropped because of "0*(5/0)"
                                        if count:tmp=(('neg',tmp[0]),*tmp[1:])if tmp else(('neg','1'),)#This needs to be the first one to keep *n working.
                                        res=(tmp[0]if tmp else'1')if len(tmp)<2 else('*n'if len(tmp)>2 else'*',*tmp)
                                    elif'-'==opchar:
                                        #if finds[0]==einds[0]:res='0'# optimisation dropped because of "5/0-5/0"
                                        if'neg'==finds[0][0]:res=('+',einds[0],finds[0][1])if'0'!=einds[0]else finds[0][1]
                                        elif'0'==finds[0]:res=einds[0]
                                        elif'0'==einds[0]:res=('neg',finds[0])
                                    elif'pos'==opchar:res=res[1]
                                    elif'neg'==opchar:
                                        if'neg'==res[1][0]:res=res[1][1]
                                        elif res[1]=='0':res='0'
                                    elif'/'==opchar:
                                        if'neg'==finds[0][0]and'neg'==einds[0][0]:res=('/',einds[0][1],finds[0][1])
                                    elif'¬'==opchar:
                                        if'¬'==res[1][0]and res[1][1][0]=='¬':res=res[1][1]
                                        if'='==res[1][0]:res=('≠',*res[1][1:])
                                        elif'≠'==res[1][0]:res=('=',*res[1][1:])
                                        elif'>'==res[1][0]:res=('≤',*res[1][1:])
                                        elif'<'==res[1][0]:res=('≥',*res[1][1:])
                                        elif'≤'==res[1][0]:res=('>',*res[1][1:])
                                        elif'≥'==res[1][0]:res=('<',*res[1][1:])
                                spinach[newind]=res
                                _log(f'FLAG! {oper=} {ops[oper]=} {finds=} {einds=} {inds=} {index=} {newind=} {spinach=}')if _log else None;
                                break
                else:break
        if endind!=startind+1 and endind!=startind:
            if funcval and'+floor+'!=funcval and'+ceil+'!=funcval:
                if funcval=='if?':
                    if(endind-startind)//2!=2:raise SyntaxError('if? ternary takes 3 arguments.')
                    spinach[startind:endind+1]=[('if?',*spinach[startind:endind+1:2])]
                elif funcval=='switch?':
                    if(endind-startind)//2<2:raise SyntaxError('switch? takes 3+ arguments.')
                    spinach[startind:endind+1]=[('switch?',*spinach[startind:endind+1:2])]
                else:spinach[startind:endind+1]=[('call',funcval,*spinach[startind:endind+1:2])]
            else:raise SyntaxError('Multiple values only valid for function calls cannot be happening here'+f' {spinach=}')
        elif funcval:
            if funcval=='if?':raise SyntaxError('if? ternary takes 3 arguments.')
            elif funcval=='switch?':raise SyntaxError('switch? takes 3+ arguments.')
            spinach[startind]=('call',funcval,spinach[startind])
        #NOTE: there was going to an optimisation for nested calls ('chaincall',(f1,f2),c...) but this was dropped for only helping in the case of chained single parameter.
    assert len(spinach)==1;return spinach[0]

def implicit_multiplication_handler(string:str)->str:"Uses some regex heuristics to try to allow implicit multiplication, but isn't perfect given debate over the precedence of implicit multiplication, and special cases such as 2ix beign ambiguously 2i*x or 2*ix";from re import sub;return sub('\\)([^\\n+^%!+‼¬*{}/≥≤≠,=><()⌊⌋⌈⌉-]+)',')*\\1',sub('([0-9)])\\(','\\1*(',sub('([0-9]+\\.[0-9]+|[0-9]+)([^\\n0-9+^%!+‼¬*{}/≥≤≠,=><()⌊⌋⌈⌉-]+)','(\\1*\\2)',string)))
def untokenise(tokens):
    'Takes a tokenised AST, and returns a text string that would tokenise equivalently. Does not handle custom brackets.'
    resq={'neg':('-',0),'pos':('+',0),'derange':('!',0),'percent':('%',1),'!':('!',1),'¬':('¬',0)};stack=[tokens];res={};otok=tokens
    while stack:
        tokens=stack.pop()
        if isinstance(tokens,str):res[tokens]=tokens;continue
        first,*p=tokens
        if'call'==first:
            f,*p=p;a=[i for i in p if i not in res]
            if a:stack.extend((tokens,*a));continue
            a=','.join(res[i]for i in p)
            for i in{*p}:res.pop(i)
            res[tokens]=f'⌊{a}⌋'if'+floor+'==f else f'⌈{a}⌉'if '+ceil+'==f else f'{f}({a})'
        elif first in resq:
            P=p[0]
            if P in res:p=res.pop(P)
            else:stack.extend((tokens,P));continue
            a,d=resq[first];a,b=('',a)if d else(a,'');r=f'{a}{p}{b}';res[tokens]=r if tokens==tokenise(r)else f'{a}({p})'
        elif'+n'==first:
            a=[i for i in p if i not in res]
            if a:stack.extend((tokens,*a));continue
            P=[res[i]for i in p];p1,p2=P[:2];p1m=f'({p1})';p2m=f'({p2})';s=f'{p1m}+{p2m}';S=tokenise(s)
            for r in(f'{p1}+{p2}',f'{p1m}+{p2}',f'{p1}+{p2m}'):
                if tokenise(r)==S:s=r;break
            for n in P[2:]:n1=f'{s}+{n}';n1m=f'{s}+({n})';s=n1 if tokenise(n1)==tokenise(n1m)else n1m
            for i in{*p}:res.pop(i)
            res[tokens]=s
        elif'*n'==first:
            a=[i for i in p if i not in res]
            if a:stack.extend((tokens,*a));continue
            P=[res[i]for i in p];p1,p2=P[:2];p1m=f'({p1})';p2m=f'({p2})';s=f'{p1m}*{p2m}';S=tokenise(s)
            for r in(f'{p1}*{p2}',f'{p1m}*{p2}',f'{p1}*{p2m}'):
                if tokenise(r)==S:s=r;break
            for n in P[2:]:n1=f'{s}*{n}';n1m=f'{s}*({n})';s=n1 if tokenise(n1)==tokenise(n1m)else n1m
            for i in{*p}:res.pop(i)
            res[tokens]=s
        elif'‼'==first:
            p,c=p
            if p in res:p=res.pop(p)
            else:stack.extend((tokens,p));continue
            res[tokens]=p+'!'*int(c)
        if'if?'==first or'switch?'==first:
            a=[i for i in p if i not in res]
            if a:stack.extend((tokens,*a));continue
            a=','.join(res[i]for i in p)
            for i in{*p}:res.pop(i)
            res[tokens]=f'{first}({a})'
        else:
            p1,p2=p
            if p1!=p2:
                if p1 not in res:stack.extend((tokens,p1));continue
                if p2 not in res:stack.extend((tokens,p2));continue
                p1=res.pop(p1);p2=res.pop(p2);p1m=f'({p1})';p2m=f'({p2})'
            else:
                if p1 not in res:stack.extend((tokens,p1));continue
                p1=p2=res.pop(p1);p1m=p2m=f'({p1})'
            for r in(f'{p1}{first}{p2}',f'{p1m}{first}{p2}',f'{p1}{first}{p2m}'):
                if tokens==tokenise(r):res[tokens]=r;break
            else:res[tokens]=f'{p1m}{first}{p2m}'
    return res[otok]#NOTE: If feels like there'd be a better solution than the general dictionary recursion pass.
def factorial(n:int)->int:
    'Computes the factorial of an integer'
    if 1==n:return 1
    if isinstance(n,float)and n.is_integer():n=int(n)
    c=[(1,n,None,[0])];cap=c.append;caw=c.pop;ind=0
    while 1:
        n,m,d,a=f=c[ind]
        if n==m:res=n
        elif m<n:res=1
        else:
            l=a[0]
            if l==2:res=a[1]*a[2]
            elif l:cap(((n+m)//2+1,m,ind,[0]));ind+=1;continue
            else:cap((n,(n+m)//2,ind,[0]));ind+=1;continue
        if d is None:return res
        else:p=c[d];p[3].append(res);caw();p[3][0]+=1;ind-=1
def nfactorial(a:int,b)->int:
    'Computes the n-factorial of an integer'
    q=1
    for i in range(a,1,-b):q*=i
    return q
basic_constants={'pow':lambda a,b,c=None:pow(a,b,c),'increment':lambda a:a+1,'min':min,'max':max,'floor':lambda a:a.__floor__(),'ceiling':lambda a:a.__ceil__(),'getthree':lambda:3,'abs':abs,'ʒ':lambda x:0*x,'iseven':lambda x:0==x%2,'nthroot':(lambda y,x:('^',x,('/','1',y)),),'sqrt':(lambda a:('^',a,('/','1','2')),),'√':(lambda x,y:('^',x,('/','1',y)),),'int':int,'nfact':nfactorial,'round':round,'pi':3.141592653589793,'tau':6.283185307179586,'e':2.718281828459045,'i':complex('j'),'one':1,'⊥':False,'⊤':True,'∞':float('inf'),'False':False,'True':True,'false':False,'true':True}
base_settings={'nfactorial':True,'nummultfunc':False,'iSymb':'i','frac/':False}
def parsen(token:str,constants:dict[str]={},fractionmode:bool=False,imaginary_token:str='i',nocrashmode:bool=False):
    'Converts a string into a useful mathematical object.'
    if fractionmode and all(i in'0123456789.'for i in token)and token.count('.')<2:return __import__('fractions').Fraction(token)
    if all(i in'0123456789'for i in token):return int(token)
    if all(i in'0123456789.'for i in token)and token.count('.')==1:return float(token)
    itl=len(imaginary_token);imtk=imaginary_token.casefold()
    if token==imtk:return 1j
    if all(i in'0123456789.'for i in token[:-itl])and 2>token.count('.')and imtk==token[-itl:].casefold():return float(token[:-1])*1j
    if token[0:2].lower()=='0b':return int(token[2:-itl],2)*1j if token[-itl:].casefold()==imtk else int(token[2:],2)
    if token[0:2].lower()=='0x':return int(token[2:-itl],16)*1j if token[-itl:].casefold()==imtk else int(token[2:],16)
    if token in constants:return constants[token]
    if nocrashmode:return None
    raise ValueError(f'Value {token!r} not understood')
assert 1230==parsen('1230');assert 1230==parsen('01230');assert .324==parsen('.324');assert 34==parsen('3nerr',{'3nerr':34});assert 1230j==parsen('1230i');assert 1230.4j==parsen('1230.4i');assert 324.==parsen('324.');assert 32.4==parsen('32.4');assert 0x234==parsen('0x234');assert 0b101==parsen('0b101');assert 0x234*1j==parsen('0x234i');assert 0b101*1j==parsen('0b101i')
def evaltokens(tokens,names:dict=basic_constants,settings=base_settings,_log=0):
    'Evaluates a given AST tree into a usable mathematical object'
    _log(f'Computing {tokens}')if _log else None
    iSymb=settings.get('iSymb','i');mfrac=settings.get('frac/',0);res={};stack=[tokens]#QUESTION: is there a better recursion method available?
    while stack:
        cur=stack[-1]
        _log(f'Evaluating: {cur}\nStack: {stack}\nKnowns: {res}')if _log else None
        oper,*data=cur
        #NOTE: I'm okay with doing isinstance str cause for dynamics like R/Python/JS there is some sort of type-of. For something like C, this'd be a "nodeval" discriminated union which can have a "isprimitive" component that is just a string, and a "operation" component that has a operator and parameter data.
        if oper in{'+n','permille','permyriad','*n','+','*','-','^','/','≥','≤','≠','=','>','<','neg','pos','¬','‼','!','mod','derange','percent'}:#NOTE: this must be synced with r_oper
            assert all(isinstance(datum,str|tuple)for datum in data)
            if all(isinstance(d,str)or d in res for d in data):
                _log(f'Combinining: {cur}')if _log else None
                parameters=(*(parsen(d,names,mfrac,iSymb)if isinstance(d,str)else res[d]for d in data),)
                for d in{d for d in data if not isinstance(d,str)}:res.pop(d)
                _log(f'Data: {parameters}')if _log else None
                if'+'==oper or'+n'==oper:comp=sum(parameters)
                elif'*'==oper:comp=parameters[0]*parameters[1]
                elif'*n'==oper:
                    comp=parameters[0]
                    for i in parameters[1:]:comp*=i
                elif'neg'==oper:comp=-parameters[0]
                elif'-'==oper:comp=parameters[0]-parameters[1]
                elif'/'==oper:comp=parameters[0]/parameters[1]
                elif'^'==oper:comp=parameters[0]**parameters[1]
                elif'mod'==oper:comp=parameters[0]%parameters[1]
                elif'!'==oper:comp=factorial(parameters[0])
                elif'percent'==oper:comp=parameters[0];comp=comp/100 if comp%100 else comp//100
                elif'≥'==oper:comp=parameters[0]>=parameters[1]
                elif'≤'==oper:comp=parameters[0]<=parameters[1]
                elif'≠'==oper:comp=parameters[0]!=parameters[1]
                elif'='==oper:comp=parameters[0]==parameters[1]
                elif'>'==oper:comp=parameters[0]>parameters[1]
                elif'<'==oper:comp=parameters[0]<parameters[1]
                elif'‼'==oper:
                    if settings.get('nfactorial',True):comp=nfactorial(parameters[0],parameters[1])
                    else:
                        q=parameters[0]
                        for i in range(parameters[1]):q=factorial(q)
                        comp=q
                elif'derange'==oper:n=parameters[0];c=1;x=[c:=c*I for I in range(1,n+1)];x.insert(0,1);b=x[-1];comp=sum(b//(v*(1,-1)[i%2])for i,v in enumerate(x))
                elif'pos'==oper:comp=+parameters[0]#NOTE: this is for custom classes support
                elif'¬'==oper:comp=not parameters[0]
                elif'permille'==oper:comp=parameters[0];comp=comp/1000 if comp%1000 else comp//1000
                elif'permyriad'==oper:comp=parameters[0];comp=comp/10000 if comp%10000 else comp//10000
                res[cur]=comp;stack.pop()
            else:stack.extend(d for d in data if not isinstance(d,str)and d not in res)
        elif'call'==oper:
            call,*data=data;assert all(isinstance(datum,str|tuple)for datum in data);flag=1
            if isinstance(call,tuple):
                _log(f'Call type recurse: {call}')if _log else None
                if call not in res:stack.append(call);flag=0
                else:call=(res[call],)
            if flag:
                if all(isinstance(d,str)or d in res for d in data):
                    _log(f'Calling: {call} on {data}')if _log else None;parameters=(*(parsen(d,names,mfrac,iSymb)if isinstance(d,str)else res[d]for d in data),)
                    for d in{d for d in data if not isinstance(d,str)}:res.pop(d)
                    _log(f'Data: {parameters}')if _log else None
                    if'+floor+'==call:ff=lambda a:a.__floor__()
                    elif'+ceil+'==call:ff=lambda a:a.__ceil__()
                    else:
                        if call in names:ff=names[call];_log(f'Function object {ff}')if _log else None
                        elif isinstance(call,tuple):ff=call[0]
                        elif settings.get('nummultfunc',False)and parsen(call,nocrashmode=1)is not None:a=parsen(call);ff=lambda c:a*c
                        else:raise NameError(f'Function {call} not defined')
                    if isinstance(ff,tuple):
                        _log('F-Substitute-Call')if _log else None;comp=ff[0](*data);_log(f'F-Call Substitution Val: {comp}')if _log else None
                        if comp in res:res[cur]=res[comp];stack.pop()
                        else:stack.append(comp)
                    else:
                        if settings.get('nummultfunc',False)and not callable(ff):_log('F-Convert')if _log else None;mult=ff;ff=lambda a:mult*a
                        _log('F-Call')if _log else None;comp=ff(*parameters);_log(f'F-Call Res: {comp}')if _log else None;res[cur]=comp;stack.pop()
                else:stack.extend(d for d in data if not isinstance(d,str)and d not in res)
        elif'if?'==oper:
            d1,d2,d3=data;assert isinstance(d1,str|tuple)and isinstance(d2,str|tuple)and isinstance(d3,str|tuple)
            if not isinstance(d1,str)and d1 not in res:stack.append(d1)
            else:
                par=d3 if(parsen(d1,names,mfrac,iSymb)if isinstance(d1,str)else res[d1])else d2
                if not isinstance(par,str)and par not in res:stack.append(par)
                else:res[cur]=parsen(par,names,mfrac,iSymb)if isinstance(par,str)else res[par];stack.pop()
        elif'switch?'==oper:
            d1,*data=data;assert isinstance(d1,str|tuple)and all(isinstance(datum,str|tuple)for datum in data)
            if not isinstance(d1,str)and d1 not in res:stack.append(d1)
            else:
                par=data[parsen(d1,names,mfrac,iSymb)if isinstance(d1,str)else res[d1]]
                if not isinstance(par,str)and par not in res:stack.append(par)
                else:res[cur]=parsen(par,names,mfrac,iSymb)if isinstance(par,str)else res[par];stack.pop()
        elif cur not in res:res[cur]=parsen(cur,names,mfrac,iSymb);stack.pop()
    return res[tokens]

def calculate(expression:str,names=basic_constants,settings=base_settings,plusbraces={}):'Calculates value of mathematical expression -- SAFE\nfuncs is a dictionary of names for functions. The function objects can be a tuple, in which case the program understands that the first item in the tuple is a function that returns a partial AST tree to substitute in.\nConstants is a list of variable names to be substituted with values.\nSettings is the basic control settings. To learn about, check the settingsdoc var.\nplusbraces is the control for the parser. The learn about, check the parserdoc var';return evaltokens(tokenise(expression,plusbraces=plusbraces),names,settings=settings)
def calc_proc(expression:str,names=basic_constants,settings=base_settings,plusbraces={}):'Same as the calculate function, but also returns the AST';a=tokenise(expression,plusbraces=plusbraces);return a,evaltokens(a,names,settings=settings)
def calc_disp(expression:str,names=basic_constants,settings=base_settings,plusbraces={}):'Same as the calculate function, but also prints';a=evaltokens(tokenise(expression,plusbraces=plusbraces),names,settings=settings);print(f'Result: {expression}={a}');return a
def calc_proc_disp(expression:str,names=basic_constants,settings=base_settings,plusbraces={}):'Same as the calculate function, but also prints with AST';a=tokenise(expression,plusbraces=plusbraces);print(f'AST: {expression} -> {a}');b=evaltokens(a,names,settings=settings);print(f'Result: {expression} = {b}');return a,b
def calc_verbose(expression:str,names=basic_constants,settings=base_settings,plusbraces={},loggingfunc=print):'The calculate function, but dumps diagnostic info';a=tokenise(expression,plusbraces=plusbraces,_log=loggingfunc);a=evaltokens(a,names,settings=settings,_log=loggingfunc);return a

examples={'1+2+3':6,'(1+2)+3':6,'1+(2+3)':6,'(1+2)+3+4':10,'(1+2)+(3+4)':10,'((1+2))+3':6,'1+2*4+3':12,'(1+2)*4+3':15,'2+(1+2)+3':8,'2+((1+2))+3':8,'10+2+3':15,'1^3':1,'-1^3':-1,'(-1)^3':-1,"3**2":9,'1+2/3':1+2/3,'1/2+3':3.5,'1^2^3':1,'(1^2)^3':1,'1+2+3>=4+5':False,'1+2+3>=4+-5':True,'1+2+3*4+-5':10,'1+2+(3*(4+2))':21,'1+2+(3*(4+2))+2':23,'abs(12)':12,'⌊342⌋':342,'4+⌊342⌋':346,'2+abs(12)':14,'abs(12)+2':14,'abs(⌊12⌋)+2':14,'abs(1+⌊12⌋+2)+2':17,'abs(floor(342))+2':344,'(12)':12,'2+(12)':14,'(2+abs(12))+2':16,'abs(2+abs(12))+2':16,'abs(abs(12))+2':14,'increment(2+abs(12))+2':17,'increment(abs(12))+2':15,'increment(abs(1))':2,'(abs(1))':1,'abs(1)':1,'max(1,2)':2,'max(1,2,3)':3,'3^3^3':7625597484987,'(3^3)^3':19683,'1+2+3+4':10,'8/4':2,'1+2+3+4/(3+1)':7,'3/(4-1)+3/(3)':2,'(3)':3,'((2))':2,'(3+2)':5,'2%':2/100,'⌊2⌋':2,"⌊2.5⌋":2,'⌈2⌉':2,"⌈2.5⌉":3,'pi':basic_constants['pi'],'∞+2':float('inf'),'∞':float('inf'),'-2':-2,'-∞':-float('inf'),'(pi)':basic_constants['pi'],'abs(-4+0)-abs(4)':0,'abs(4)':4,'abs(-4)':4,'((5))':5,'12+4':16,'12*(3-(1+1)+4)':60,'12+4.5':16.5,'12+(-4)^0.5':12+2j,'12+(-3)^0.5':12+1.7320508075688772j,'!5':44,'5++2':7,'5--2':7,'5---2':3,'5+-2':3,'5-+2':3,'12/4':3.0,'5/3':5/3,'3^2^3':6561,'5!':120,'5-4':1,'3.4':3.4,'100%7':100%7,'100mod7':100%7,'nthroot(4,6561)':9.0,'abs(4-abs(3+2))':1,'4=4':True,'1=2':False,'1>2':False,'1<2':True,'2≥2':True,'2≤2':True,'2>2':False,'2<2':False,'2≠2':False,'2≠3':True,'3+'*10+'3':33,'3+'*100+'3':303,'3+'*200+'3':603,'3+'*141+'3':426,'3+'*1000+'3':3003,'3*'*30+'3':617673396283947,'abs('*100+'3'+')'*100:3,'abs('*1000+'3'+')'*1000:3,'(((((((((((((((((((((3)))))))))))))))))))))':3,'12*(3-(1+(3-2*(1^1)+0*(2+2)))+4)':60,"abs(4)+pi":4+basic_constants['pi'],"abs(pi)":basic_constants['pi'],"¬1":0,"¬0":1,"(1+2*i)^2":-3+4j,"(1+2i)^2":-3+4j,"nthroot(1+1,64)":8,'1^(-1)':1,'1^-1':1,'3^-4':3**-4,'3!!':3,('3!!',(('nfactorial',False),)):720,('2(2)',(('nummultfunc',True),)):4,'.1+.2=.3':False,('.1+.2=.3',(('frac/',True),)):True,'(3!)!':720,'12!!!+2':1946,'3!%':.06,'300%!':6,'1‰':1/1000,'1‱':1/10000,'2!^!3':4,'2%^3':.02**3,'2%^!3':.02**2,'2!^-3':1/8,'10!!!^3':21952000,'10!!!^!3':78400,'4^--3':64,'3^!!2':1,'3%^--2':.03**2,'3%%^--2':.0003**2,'3!%%^--2':.0006**2,'3!!!%%^--2':.0003**2,'3%!%^--2':.0001,'3%%!%%^--2':.0001**2,'30000%%!!!%%^--2':.0003**2}
errorcases=('2n','n(2)','2(n)','2-*3','2-/3','3/','3*','3-','3+','*3','/3','n!','n3n','(2+3','32-2)','(23)/(2','32)/2','(32/2','we\\23','23\\23','23//4','3***5','2///4','(2+2)(4)','(a+b)(2)','23,4',"abs⌊342⌋+2")

settingsdoc='The evaluator settings currently recognises 4 values:\n\tThe "nfactorial" setting is a boolean value determining how repeated factorial marks are handled, as either repeated factorial or as n-factorials\n\tThe "nummultfunc" parameter is a boolean parameter that determins if function calling an integer (e.g. "12(expr)") is treated as 12*expr\n\tThe "frac/" boolean parameter (Python Only) controls if the program uses a fractional system instead of floats. Using it on non-Python versions is undefined behaviour.\n\tThe "iSymb" parameter (Python Only) controls what character at the end of a numeric literal maps to imaginary numbers. Using it on non-Python versions is undefined behaviour.'
parserdoc='The parser currently only recognises 2 optional brackets, "{}" and "[]". Pass them in with the dictionary with a value of None to allow them to be treated similarly to parentheticals. If a string is passed, then the brackets are treated as bracket operators. Bracket operators cannot have a function bound to them, and execute the named function during evaluation.  only accepts keys of "[]" & "{}". it is recommended that the given gracket function names start and end with + to distiguish them from ordinary function calls. This does mean that untokenise will be unable to operate properly.  (--optimise)'

def sympymode():
    'Turns on sympy for the evaluator';import sympy;global parsen;base_funcs.update({'pow':lambda a,b,c=None:(sympy.Pow(a,b)if c is None else sympy.Mod(sympy.Pow(a,b,0),c)),'getthree':lambda:sympy.Rational(3),'abs':lambda x:sympy.Abs(x),'ʒ':lambda x:0*x,'iseven':lambda x:0==x%2,'nthroot':lambda y,x:[['^',x,['/',1,y]]],'√':lambda x,y:[['^',x,['/',1,y]]],'int':lambda x:sympy.Rational(int(x))});basic_constants.update({'pi':sympy.pi,'e':sympy.E,'tau':sympy.pi*2,'i':sympy.I,'one':sympy.Rational(1),'∞':sympy.oo})
    def parsen(token:str,constants:dict[str]={},fractionmode:bool=False,imaginary_token:str='i',nocrashmode:bool=False):
        if all(i in'0123456789.'for i in token)and token.count('.')<2:return sympy.Rational(token)
        itl=len(imaginary_token);imtk=imaginary_token.casefold();II=sympy.I
        if token==imtk:return II
        if all(i in'0123456789.'for i in token[:-itl])and 2>token.count('.')and imtk==token[-itl:].casefold():return sympy.Rational(token[:-1])*II
        if token[0:2].lower()=='0b':return int(token[2:-itl],2)*II if token[-itl:].casefold()==imtk else sympy.Rational(int(token[2:],2))
        if token[0:2].lower()=='0x':return int(token[2:-itl],16)*II if token[-itl:].casefold()==imtk else sympy.Rational(int(token[2:],16))
        if token in constants:return constants[token]
        if nocrashmode:return None
        raise ValueError(f'Value {token!r} not understood')

if'__main__'==__name__:
    bb=1;print('Running Validation suite')
    for i,v in examples.items():
        try:
            R=calculate(i)if isinstance(i,str)else calculate(i[0],settings=dict(i[1]));c=R==v
            if not c:bb=0;print(f'ERROR: {i} computes to {R} when it should be {v}, tree {tokenise(i)}')
        except Exception:bb=0;print(f'MAJOR ERROR!!: {i} fails',tokenise(i))
        #else:print(f'Valid: {i}={R}')
    print('No Errors!'if bb else'Errors!!!!')

    curbraces={'--optimise':0};cursetting={**base_settings};viewermode=0
    while 1:
        a=input('>');A=a.lower().strip()
        if''==A:print('Empty Statement. Try help!')
        elif'help'==A or'?'==A:print('sympy/sympymode/mathmode for activating sympy\nTo modify settings, viewsetting/toptimise/tnfactorial/tnummultfunc/tfracmode\nToggle view mode using tview')
        elif'quit'==A or'exit'==A:break
        elif'tview'==A:viewermode^=1
        elif'toptimise'==A:curbraces['--optimise']^=1
        elif'tnfactorial'==A:cursetting['nfactorial']^=1
        elif'tnummultfunc'==A:cursetting['nummultfunc']^=1
        elif'tfracmode'==A:cursetting['frac/']^=1
        elif'viewsetting'==A:print(curbraces,cursetting,viewermode)
        elif'sympy'==A or'sympymode'==A or'mathmode'==A:print('Loading sympy...');sympymode();print('loaded')
        else:
            try:(calc_proc_disp if viewermode else calc_disp)(a,plusbraces=curbraces,settings=cursetting)
            except Exception:import traceback;traceback.print_exc()
#NOTE: I've decided to be okay with both functions/classes being first class objects and using callable because that works in a dynamically typed (if no test for callability then assume it isn't) scenario, and in a static type either the superunion value type support functions, or they can split names into functions and values.
#I'd hate to have to get unicode support wokring in other langs.

#The "-0" → "0" optimisation is purely a pet peeve of mine. Otherwise I'd allow the 0%=0‰=0‱→0 optimisation and the "number-samenumber=0" and the "a%% → a‱" optimisations.

#NOTE: I chose to reject notation like abs⌊a⌋ for some reason. It wouldn't even be hard to support!
