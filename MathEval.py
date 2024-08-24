r'''The Definitive* Order Of Operations

RTL=Right-To-Left

(,) 0 Parenthesis → Isolates part of the expression to be locally pre-computed before being evaluated by the rest of the expression
 |  0 Absolute Value Bars → Similar to parentheses, returns the absolute value of the inner expression, sometimes ambiguous as to what is in/out of it
 ^  1 Exponents → RTL
()root()/√ 0 Roots → as it defines captures by parentheses
|> ·/*/x 2 Multiplication
|-1	→ Implicit Multiplication → muddy waters…
|> \/ 2 Division

|> + 3 Addition
|-1
|> - 3 Subtraction


*! 1.4 Factorial - just above negation
func() 0 Functions(Parenthetical) = direct modification of parenthetical value
+ 1.5 plus = RTL, same as negation except it does nothing
- 1.5 negation = RTL, just below exponents
mod|% 1.6 Modulo
% 1.4 Percent'''

'''
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
'''
_base_funcs={'pow':lambda a,b,c=None:pow(a,b,c),'getthree':lambda:3,'abs':lambda x:abs(x),'ʒ':lambda x:0*x,'iseven':lambda x:0==x%2,'nthroot':lambda y,x:[['^',x,['/',1,y]]],'√':lambda x,y:[['^',x,['/',1,y]]],'int':lambda x:int(x),'sqrt':lambda a:['^',a,['/',1,2]]};_base_conts={'pi':3,'i':complex('j'),'one':1,'⊥':False,'⊤':True,'∞':float('inf')}
processor_settings={
"multifactorial":False,
"implicit_multiplication_handler":False,
"braces_fractional":True
}
def implicit_multiplication_handler(string:str)->str:from re import sub;return sub('\\)([^+^%!+‼¬*{}/≥≤≠,=><()⌊⌋⌈⌉-]+)',')*\\1',sub('([0-9)])\\(','\\1*(',sub('([0-9]+)([^0-9+^%!+‼¬*{}/≥≤≠,=><()⌊⌋⌈⌉-]+)','(\\1*\\2)',string)))
def _tokenize(string:str,_log=0,processor_settings=processor_settings)->list:
    _log('Tokenizing "{}"\nFiltering',string)if _log else None;string=string.replace(' ','').replace('**','^').replace('⋅','*').replace('!=','≠').replace('÷','/').replace('>=','≥').replace('<=','≤').replace('mod','%').replace('‼','!!')
    while"--"in string:string=string.replace('--','+')
    while"++"in string:string=string.replace('++','+')
    while"+-"in string:string=string.replace('+-','-')
    while"-+"in string:string=string.replace('-+','-')
    if processor_settings.get('implicit_multiplication_handler',0):string=implicit_multiplication_handler(string)
    if processor_settings.get('multifactorial',0):
        while'!!'in string:
            a=b=string.find('!!')
            while b!=len(string)and'!'==string[b]:b+=1
            string=f'{string[:a]}‼{b-a}{string[b:]}'
    _log('log info filter +/- result {}',string)if _log else None;par_expr=[];j=0
    operators=[
        (-1,
            (('^','^'),1,-1)
        ),
        (1,
            (('%','percent'),('!','!'),-1,1.0)
        ),
        (1,
            (('‼','‼'),1,-1)
        ),
        (1,
            (('+','pos'),('-','neg'),1,-1.0)
        ),
        (1,
            (('!','derange'),('¬','¬'),1,-1.0)
        ),
        (1,
            (('*','*'),('/','/'),('%','mod'),1,-1)
        ),
        (1,
            (('+','+'),('-','-'),1,-1)
        ),
        (1,
            (('≥','≥'),('≤','≤'),('≠','≠'),('=','='),('>','>'),('<','<'),1,-1)
        ),
    ]
    brackets=(
        ('()',None),
        ('⌊⌋','floor'),
        ('⌈⌉','ceil'),
    )
    _=processor_settings.get('braces_fractional',0)
    if _:brackets=(*brackets,('{}','fractional'if _==1 else None))
    r_oper={*[item[0]for sublist in operators for item in sublist[1]if isinstance(item,tuple)and isinstance(item[0],str)],','};funcbreakers={*r_oper,*(j for i,v in brackets for j in i)};funccatch={};s_br={i[0][0]for i in brackets};e_br={i[0][1]for i in brackets};s_brd={i[0][0]:(i[0][1],i[1])for i in brackets};nodes={None:[string]};current=[None]
    while current:
        _log('Data: {}\nTo process: {}',nodes,current)if _log else None;a=current.pop();string=nodes[a][0];pairend=pairstart=None;_log('Processing: {}/{}',a,string)if _log else None
        if isinstance(string,tuple):func,string=string;_log(f'IsFunc\n{func} : {string}')if _log else None
        else:func=None
        matches=[];level=0;foundfunc=None;res=[];cur=[];brfu=None
        for i,v in enumerate(string):
            if pairstart is None:
                if v in s_br:
                    _log('Bracket start: "{}"\nScanning for preceding function',v)if _log else None
                    pairstart=v;
                    if i>0:
                        i-=1;c=0
                        while string[i]not in funcbreakers and i>=0:i-=1;c+=1
                        i+=1
                    else:c=0
                    _log('Function found'if c else'No function')if _log else None;cur=cur[:-c]if c else cur;matches.append((c,i));pairend,foundfunc=s_brd[pairstart];_log('ID bracket ending({}) and func({})',pairend,foundfunc)if _log else None
                    if c and foundfunc is not None:raise SyntaxError(f'Bracket {v} doesn\'t support functions')
                    res.append(''.join(cur));cur.clear()
                elif v in e_br:raise SyntaxError(f'Bracket End {v} missing Start Symbol')
                else:cur.append(v)
            elif v==pairstart:level+=1;_log('Subbracket level #{} detected - noting',level)if _log else None
            elif v==pairend:
                if level:level-=1;_log('Subbracket level #{} ended',level)if _log else None
                else:matches[-1]=(*matches[-1],i+1,foundfunc);pairend=pairstart=None;_log('End Of Bracket - {} to {}',matches[-1][1],i+1)if _log else None
        res.append(''.join(cur))
        if matches and 2==len(matches[-1]):raise SyntaxError(f'Bracket {pairstart} at {matches[-1][1]} was never closed')
        d=[];_log('Scanning brackets')if _log else None;matches=[[(string[i:i+c],string[i+c+1:v-1])if c else(string[i+1:v-1]if d is None else(d,string[i+1:v-1]))]for c,i,v,d in matches];_log('Creating bracket nodes',level)if _log else None
        for l,i in enumerate(matches):
            if i[0]in nodes:matches[l]=nodes[i[0]];_log('grabbing preexisting data ref for {}',i)if _log else None
            else:nodes[i[0]]=i;current.append(i[0]);_log('appending node {}',i)if _log else None
        _log('re-integrating brackets and (other) stuff')if _log else None
        for i,v in zip(res,matches):d.extend((i,v))
        if len(res)>len(matches):d.append(res[-1])
        d=[i for i in d if''!=i];c=[];_log('splitting operators in {}',d)if _log else None
        for i in d:
            if isinstance(i,str):
                cc=[]
                for j in i:
                    if j in r_oper:c.append(''.join(cc));_log('Operator {} detected in {}: front part is {}',j,i,cc)if _log else None;c.append(j);cc.clear()
                    else:cc.append(j)
                c.append(''.join(cc))
            else:c.append(i)
        x=[i for i in c if''!=i];_log('tree branching by operators in {}',x)if _log else None
        for _dir,*op in operators:
            op,opmap=[(*(ii[0]if isinstance(ii,tuple)else ii for ii in i),)for i in op],{ii[0]:ii[1]if ii[1]is not None else ii[0]for i in op for ii in i if isinstance(ii,tuple)};op=[i for i in op if any(ii in x for ii in i)]
            if[]==op:continue
            looper=range(len(x))if _dir==1 else range(len(x)-1,-1,-1);opdict={(*(ii for ii in i if isinstance(ii,str)),):frozenset([ii for ii in i if isinstance(ii,int|float)])for i in op};ops=[item for sublist in opdict for item in sublist];v=1
            while v:
                for index in looper:
                    v=0
                    if x[index]in ops:
                        j=[i for i in opdict if x[index]in i][0];para=opdict[j];c=[];para,exc=[i for i in para if isinstance(i,int)],[int(i)for i in para if isinstance(i,float)]
                        for iii in para:
                            if not 0<=index+iii<len(x)or(not isinstance(x[index+iii],list|tuple)and x[index+iii]in r_oper):c=0;break
                            c.append(x[index+iii])
                        for iii in exc:
                            if 0<=index+iii<len(x)and(isinstance(x[index+iii],list|tuple)or x[index+iii]not in r_oper):c=0;break
                        if c:
                            c.reverse();x[index]=[opmap[x[index]],*c]
                            for iii in sorted(para,reverse=1):x.pop(index+iii)
                            looper=range(len(x))if _dir==1 else range(len(x)-1,-1,-1);v=1
                    if v:break
        _log('handling mainfunc')if _log else None;d=[i[0]if isinstance(i,list)and isinstance(i[0],list)and 1==len(i)else i for i in x if''!=i]
        if not d and func is None:raise SyntaxError(f'An empty statement is invalid')
        if all(not isinstance(i,list)and(i in r_oper)for i in d)and func is None:raise SyntaxError("No numbers - just operators")
        if len(d)>1:
            if func is None:raise SyntaxError("Probably missing an operator")
            else:
                pcount=d.count(',');d=[i for i in d if','!=i]
                if pcount+1!=len(d):raise SyntaxError('Error: Missing operator/comma')
        _log('saving data')if _log else None;nodes[a][0]=d if func is None else(func,d)
    nodes=nodes[None]
    while 1==len(nodes)and isinstance(nodes[0],list):nodes=nodes[0]
    return nodes
#TODO: proper math parser char by char

def _untokenize(tokens)->str:
    #print(tokens)
    "Generates string that produces similar tokens";santa={'^':'{}^{}','≥':'{}≥{}','≤':'{}≤{}','≠':'{}≠{}','=':'{}={}','>':'{}>{}','>':'{}>{}','-':'{}-{}','+':'{}+{}','*':'{}*{}','/':'{}/{}','mod':'{}%{}','pos':'+{}','neg':'-{}','¬':'¬{}','derange':'!{}','percent':'{}%','!':'{}!'};from copy import deepcopy;current=[deepcopy(tokens)]
    def laber(a):return isinstance(a,str|int)or(isinstance(a,list)and 1==len(a)and isinstance(a[0],str|int))
    def marko(a):return f'{a[0]}'if isinstance(a,list)else a
    while current:
        lar=current[-1]
        #print(f'{current=}\ntype={type(lar)} {lar=}')
        #input()
        if isinstance(lar,list):
            if isinstance(lar[0],tuple):
                das=lar[0][1]
                if not laber(das):current.append(das);continue
                lar[0]=f'{lar[0][0]}({marko(das)})';current.pop();continue
            dd=1
            for i in range(1,len(lar)):
                if not laber(lar[i]):current.append(lar[i]);dd=0
            if dd:
                if len(lar)>1:
                    if lar[0]in santa:
                        #NOTE: patch measure. Will wait for fix to MathEval before attempting proper computation
                        cc1=santa[lar[0]].format(*(f'({marko(i)})'for i in lar[1:]))
                        cc2=santa[lar[0]].format(*(f'{marko(i)}'for i in lar[1:]))
                        cc=cc2 if _tokenize(cc1)[0]==_tokenize(cc2)[0]else cc1
                    else:cc=','.join(marko(i)for i in lar)
                elif not laber(lar):cc=lar[0];lar.clear();lar.extend(cc);continue
                else:cc=lar[0]
                lar.clear();lar.append(cc);current.pop()
    return lar[0]

def _mathify(ans,f=0):
    if f:from fractions import Fraction;v=complex(ans)if isinstance(ans,complex)else Fraction(ans)
    else:
        if isinstance(ans,str)and all(i in'-0123456789.'for i in ans[:-1])and'i'==ans[-1].lower():
            v=float(ans[:-1])*1j
        else:
            try:ff=0;v=ans if isinstance(ans,int)or isinstance(ans,complex)else(int(ans)if isinstance(ans,str)and'.'not in ans else float(ans))
            except ValueError:ff=1
            if ff:raise ValueError(f'Could not parse "{ans}" as a number.')
    return v
def factorial(n:int)->int:
    if 1==n:return 1
    if isinstance(n,float)and n.is_integer():n=int(n)
    c=[(1,n,None,[0])];cap=c.append;caw=c.pop;ind=0
    while c:
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
    q=1
    for i in range(a,1,-b):q*=i
    return q
_base_funcs['nfact']=nfactorial
def _evaluate(tokens,f:bool=0,funcs:dict=_base_funcs,constants:dict=_base_conts,_log=0)->'number':
    funcs.update({'ceil':lambda x:x.__ceil__(),'floor':lambda x:x.__floor__(),'fractional':lambda x:['mod',x,1]});cil=len(tokens);layers=[tokens];_log('Evaluating {}',tokens)if _log else None
    def getval(a):return constants[a]if a in constants else _mathify(a,f)
    def numericyesno(a):
        while isinstance(a,list|tuple)and 1==len(a):a=a[0]
        return a if not isinstance(a,list)else None
    def duo(a):
        if len(a)!=2:raise SyntaxError('Parsing Error - more than two parameters for binary operator')
    def funchand(a):
        _log('\nF-call\n')if _log else None;f,p=a[0];_log('a={}\t\tFunction: {}, Parameters: {}',a,f,p)if _log else None;
        c=[getval(i)if isinstance(i,str)else i for i in[numericyesno(i)for i in p]]
        if all(i is not None and not isinstance(i,tuple)for i in c):
            if f in funcs:a[0]=funcs[f](*c);_log('Function {}{}={}',f,c,a[0])if _log else None
            else:raise ValueError(f'Function {f} not defined')
        else:_log('Processing Parameters {}',p)if _log else None;layers.append(['fpar',*p])
    while layers:
        curlay=layers[-1];_log('\nProcessing layer data: current_layer={}\t\tmains={}  layers={}',curlay,tokens,layers)if _log else None
        if len(curlay)==1:
            d=numericyesno(curlay[0])
            _log('Processing singular - {}',d)if _log else None
            if d is None:layers.append(curlay[0]);_log('Entering another layer')if _log else None;continue
            elif isinstance(d,tuple):curlay[0]=c=[d];_log('Entering function')if _log else None;funchand(c)
            else:curlay[0]=(getval(d),);_log('Computed value of {} as {}',d,curlay[0])if _log else None;layers.pop()
        elif'fpar'==curlay[0]:
            _log('Handling function parameters {}',curlay)if _log else None
            for l,i in enumerate(curlay[1:],1):
                d=numericyesno(i);_log('Data: {}  Node: {}',d,i)if _log else None
                if d is None:d=[i];curlay[l]=d;layers.append(d);_log('Parameter Dive')if _log else None;break
                elif isinstance(d,tuple):_log('SF Call\ni={} d={}',i,d)if _log else None;funchand(i);break
            else:layers.pop();_log('parameters all valid')if _log else None
            _log('Handled function parameters {}',curlay)if _log else None
        else:
            op,*b=curlay;trip=0;_log('Computing operation {} on numbers with {}',op,b)if _log else None
            for v,a in enumerate(b):
                _log('Checking parameter at {}: {}',v,a)if _log else None
                if isinstance(a,str):b[v]=getval(a);_log('parameter was numerfied')if _log else None
                elif isinstance(a,list):
                    if isinstance(a[0],tuple):
                        if len(a[0])==1:b[v]=a[0][0];_log('parameter is numeric')if _log else None
                        else:curlay[v+1]=d=[a[0]];funchand(d);trip=1;_log('parameter is subfunction - must process first')if _log else None;break
                    else:layers.append(a);trip=1;_log('processing inner data')if _log else None;break
                _log('parameters: {}',b)if _log else None
            if trip:_log('Diving')if _log else None;continue
            if'+'==op:res=sum(b)
            elif'*'==op:duo(b);res=b[0]*b[1]
            elif'-'==op:duo(b);res=b[0]-b[1]
            elif'^'==op:duo(b);res=b[0]**b[1]
            elif'/'==op:duo(b);res=b[0]/b[1]
            elif'≥'==op:res=all(b[0]>=ii for ii in b)
            elif'≤'==op:res=all(b[0]<=ii for ii in b)
            elif'≠'==op:res=all(b[0]!=ii for ii in b[1:])
            elif'='==op:res=all(b[0]==ii for ii in b)
            elif'>'==op:res=all(b[0]>ii for ii in b[1:])
            elif'<'==op:res=all(b[0]<ii for ii in b[1:])
            elif'neg'==op:
                if len(b)==1:res=-b[0]
                else:raise SyntaxError("Honestly, I don't know how you tricked by program into recognising multiple parameters for negation. Something has gone horribly wrong - please file a bug request")
            elif'pos'==op:
                if len(b)==1:res=b[0]
                else:raise SyntaxError("Honestly, I don't know how you tricked by program into recognising multiple parameters for positivation. Something has gone horribly wrong - please file a bug request")
            elif'¬'==op:
                if len(b)==1:res=not b[0]
                else:raise SyntaxError("Honestly, I don't know how you tricked by program into recognising multiple parameters for ¬. Something has gone horribly wrong - please file a bug request")
            elif'‼'==op:duo(b);res=nfactorial(b[0],b[1])
            elif'!'==op:
                if len(b)==1:res=factorial(b[0])
                else:raise SyntaxError("Honestly, I don't know how you tricked by program into recognising multiple parameters for factorial. Something has gone horribly wrong - please file a bug request")
            elif'mod'==op:duo(b);res=b[0]%b[1]
            elif'derange'==op:
                if len(b)==1:
                    n=b[0];c=1;x=[c:=c*I for I in range(1,n+1)];x.insert(0,1);b=x[-1];res=sum([b//(v*(-1)**i)for i,v in enumerate(x)])
                else:raise SyntaxError("Program id'd operator as \"derangement\", but found multiple parameters. Please file a bug request")
            elif'percent'==op:
                if len(b)==1:res=b[0]/100
                else:raise SyntaxError("Probably modulo misidentified as percent. Please file a bug request")
            else:raise SyntaxError(f'Operator "{op}" not recognized')
            curlay.clear();curlay.append(res)
    return tokens[0][0]
def calculate(expression:str,precise:bool=False,funcs=_base_funcs,constants=_base_conts,processor_settings=processor_settings)->'number':'Calculates value of mathematical expression -- SAFE\n\nprecise allows for precision via fractions module\n\nfunctions and constants, eg: abs & pi can be set via funcs & constants respectively';return _evaluate(_tokenize(expression,processor_settings=processor_settings),precise,funcs=funcs,constants=constants)
def calc_proc(expression:str,precise:bool=False,funcs=_base_funcs,constants=_base_conts,processor_settings=processor_settings)->'number':print(v:=_tokenize(expression,processor_settings=processor_settings));print(v:=_evaluate(v,precise,funcs=funcs,constants=constants));return v
def calc_disp(expression:str,precise:bool=False,funcs=_base_funcs,constants=_base_conts,processor_settings=processor_settings):'Calculates value of mathematical expression and prints';print(expression,'=',_evaluate(_tokenize(expression,processor_settings=processor_settings),precise,funcs=funcs,constants=constants))
def calc_verbose(expression:str,precise:bool=False,funcs=_base_funcs,constants=_base_conts,processor_settings=processor_settings,loggingfunc=print)->'number':
    'Dumps Diagnostic Info'
    def log(string,*data):loggingfunc(string.format(*data))
    v=_tokenize(expression,_log=log,processor_settings=processor_settings);c=_evaluate(v,precise,funcs=funcs,constants=constants,_log=log);return c

def sympymode():
    import sympy;global _mathify,_base_funcs,_base_conts;_base_funcs={'pow':lambda a,b,c=None:(sympy.Pow(a,b)if c is None else sympy.Mod(sympy.Pow(a,b,0),c)),'getthree':lambda:sympy.Rational(3),'abs':lambda x:sympy.Abs(x),'ʒ':lambda x:0*x,'iseven':lambda x:0==x%2,'nthroot':lambda y,x:[['^',x,['/',1,y]]],'√':lambda x,y:[['^',x,['/',1,y]]],'int':lambda x:sympy.Rational(int(x))};_base_conts={'pi':sympy.pi,'i':sympy.I,'one':sympy.Rational(1),'⊥':False,'⊤':True,'∞':sympy.oo}
    def _mathify(ans,f=0):
        if isinstance(ans,str):
            if all(i in'-0123456789.'for i in ans):v=sympy.Rational(ans)
            elif all(i in'-0123456789.'for i in ans[:-1])and'i'==ans[-1].lower():v=sympy.Rational(ans[:-1])*sympy.I
            elif all(i in'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'for i in ans):v=sympy.Symbol(ans)
            else:v=sympy.nan
        elif isinstance(ans,int):v=sympy.Rational(ans)
        else:v=ans
        return v
#TODO: primorial?

examples={'1+2+3+4':10,'8/4':2,'1+2+3+4/(3+1)':7,'3/(4-1)+3/(3)':2,'(3)':3,'((2))':2,'(3+2)':5,'2%':2/100,'⌊2⌋':2,"⌊2.5⌋":2,'⌈2⌉':2,"⌈2.5⌉":3,'pi':3,'∞+2':float('inf'),'∞':float('inf'),'-2':-2,'-∞':-float('inf'),'(pi)':3,'abs(-4+0)-abs(4)':0,'abs(4)':4,'abs(-4)':4,'((5))':5,'12+4':16,'12*(3-(1+1)+4)':60,'12+4.5':16.5,'12+(-4)^0.5':12+2j,'12+(-3)^0.5':12+1.7320508075688772j,'!5':44,'5++2':7,'5--2':7,'5+-2':3,'5-+2':3,'12/4':3.0,'5/3':5/3,'3^2^3':6561,'5!':120,'5-4':1,'3.4':3.4,'100%7':100%7,'nthroot(4,6561)':9.0,'abs(4-abs(3+2))':1,'4=4':True,'1=2':False,'1>2':False,'1<2':True,'2≥2':True,'2≤2':True,'2>2':False,'2<2':False,'2≠2':False,'2≠3':True,'3+'*10+'3':33,'3+'*100+'3':303,'3+'*200+'3':603,'3+'*141+'3':426,'3+'*1000+'3':3003,'3*'*30+'3':617673396283947,'abs('*100+'3'+')'*100:3,'(((((((((((((((((((((3)))))))))))))))))))))':3,'12*(3-(1+(3-2*(1^1)+0*(2+2)))+4)':60,"abs(4)+pi":7,"abs(pi)":3,"¬1":0,"¬0":1,"(1+2*i)^2":-3+4j,"(1+2i)^2":-3+4j,"nthroot(1+1,64)":8}
if'__main__'==__name__:
    bbb=True
    for i,v in examples.items():
        #print(calculate(i)==v,calculate(i),i,_tokenize(i))
        aaa=(ccc:=calculate(i))==v;print('  Valid'if aaa else'Invalid','\t',i[:100]);bbb=bbb and aaa
        if not aaa:print(f'Error Val {v=} {ccc=}')
        #v=_untokenize(_tokenize(i))
        #print(v,_tokenize(v))
        print()
        #print(i,_tokenize(i));calc_verbose(i)if'y'==input()else''
    print('No Errors'if bbb else'Errors!');print('Note: MathEval uses floating-point numbers, so radicals and other numbers may be off.\nIf you want precise math, MathEval has a mode activated by "sympymode()"')

errorcases=['2n','2(2)','n(2)','2(n)','2-*3','2-/3','3/','3*','3-','3+','*3','/3','n!','n3n','(2+3','32-2)','(23)/(2','32)/2','(32/2','we\\23','23\\23','23//4','3***5','2///4','(2+2)(4)','(a+b)(2)','23,4']



"Independent code copies: TimerScriptV2.py , unitconverty mobile"
"And the JS port"
