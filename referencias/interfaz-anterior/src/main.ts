import {Component} from '@angular/core';
import {bootstrapApplication} from '@angular/platform-browser';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
interface Course {id:string;name:string;level:number;credits:number;elig:string;req:string;capacity:number;demand:number;}
@Component({selector:'app-root',standalone:true,imports:[FormsModule,CommonModule],templateUrl:'./app.html'})
class App {
 page='Preinscripción'; tabs=['Inicio','Preinscripción','Reconfirmación','Demanda']; query='';level='Todos'; role='Estudiante';status='Borrador';selected:string[]=[];confirmed:string[]=[];priority:Record<string,string>={};message='';consent=false;modal=false;reason='';history:string[]=[];
 courses:Course[]=[
 {id:'ECMC1023',name:'REDES',level:5,credits:3,elig:'Verificada',req:'Arquitectura de computadores',capacity:25,demand:43},
 {id:'ECMC1024',name:'SISTEMAS OPERATIVOS',level:5,credits:3,elig:'Verificada',req:'Estructuras de datos',capacity:30,demand:37},
 {id:'ECMC1025',name:'BASE DE DATOS',level:5,credits:3,elig:'Verificada',req:'Programación avanzada',capacity:30,demand:39},
 {id:'ECMC1026',name:'APLICACIONES WEB',level:6,credits:3,elig:'Condicional',req:'Base de datos (en curso)',capacity:25,demand:31},
 {id:'ECMC1027',name:'AGENTES INTELIGENTES',level:6,credits:3,elig:'Desconocida',req:'Sin historial autorizado',capacity:25,demand:22},
 {id:'ECMC1028',name:'SISTEMAS DISTRIBUIDOS',level:6,credits:3,elig:'Condicional',req:'Redes (en curso)',capacity:20,demand:28},
 {id:'ECMC1029',name:'INGENIERÍA DE SOFTWARE',level:6,credits:3,elig:'Verificada',req:'Programación avanzada',capacity:30,demand:26},
 {id:'ECMC1030',name:'COMPUTACIÓN GRÁFICA',level:7,credits:3,elig:'Desconocida',req:'Sin historial autorizado',capacity:20,demand:18}];
 constructor(){try{const s=JSON.parse(localStorage.getItem('previa-v1')||'null');if(s&&Array.isArray(s.selected)&&s.selected.every((id:unknown)=>this.courses.some(c=>c.id===id))&&new Set(s.selected).size===s.selected.length&&['Borrador','Enviada','Retirada'].includes(s.status)){this.selected=s.selected;this.status=s.status;this.priority=s.priority||{};this.confirmed=Array.isArray(s.confirmed)?s.confirmed.filter((id:string)=>this.selected.includes(id)):[];this.history=Array.isArray(s.history)?s.history:[];}}catch{}}
 get filtered(){return this.courses.filter(c=>(c.name+' '+c.id).toLowerCase().includes(this.query.toLowerCase())&&(this.level==='Todos'||c.level===+this.level));}
 get chosen(){return this.courses.filter(c=>this.selected.includes(c.id));} get credits(){return this.chosen.reduce((n,c)=>n+c.credits,0);}
 go(p:string){this.page=p;this.message='';}
 persist(){try{localStorage.setItem('previa-v1',JSON.stringify({selected:this.selected,status:this.status,priority:this.priority,confirmed:this.confirmed,history:this.history}));}catch{this.message='El navegador no permite guardar; el estado dura solo esta sesión.';}}
 toggle(id:string){if(this.status==='Enviada')return;this.selected=this.selected.includes(id)?this.selected.filter(x=>x!==id):[...this.selected,id];this.status='Borrador';this.confirmed=[];this.persist();}
 save(){this.persist();this.message='Borrador guardado. Todavía no contribuye al informe de demanda.';}
 submit(){if(!this.selected.length||!this.consent)return;this.status='Enviada';this.modal=false;this.history.unshift('Intención enviada · '+new Date().toLocaleString('es-EC'));this.persist();this.message='Intención enviada. No reserva cupos ni constituye matrícula oficial.';}
 withdraw(){this.status='Retirada';this.confirmed=[];this.history.unshift('Intención retirada · '+new Date().toLocaleString('es-EC'));this.persist();this.message='Solicitud retirada del conteo de demanda. Puedes modificarla y volver a enviarla.';}
 demand(c:Course){return c.demand+(this.status==='Enviada'&&this.selected.includes(c.id)?1:0);}
 recon(id:string){this.confirmed=this.confirmed.includes(id)?this.confirmed.filter(x=>x!==id):[...this.confirmed,id];}
 reconfirm(){if(this.status!=='Enviada'||!this.confirmed.length||(this.confirmed.length!==this.selected.length&&!this.reason.trim()))return;this.history.unshift('Reconfirmación de matrícula (simulación): '+this.confirmed.join(', ')+' · '+(this.reason||'Sin cambios'));this.persist();this.message='Reconfirmación guardada. La intención original se conserva.';}
 download(type:string){let data='',name='';if(type==='csv'){data='Código,Asignatura,Demanda enviada,Capacidad de referencia,Brecha\n'+this.courses.map(c=>[c.id,c.name,this.demand(c),c.capacity,this.demand(c)-c.capacity].join(',')).join('\n');name='demanda-previa.csv';}else{data='PREVIA · SIMULACIÓN — NO ES MATRÍCULA\nEstado: '+this.status+'\n'+this.chosen.map(c=>c.id+' '+c.name+' | Prioridad: '+(this.priority[c.id]||'Alta')).join('\n')+'\nReconfirmadas: '+this.confirmed.join(', ');name='preinscripcion-previa.txt';}const url=URL.createObjectURL(new Blob(['\uFEFF'+data],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);}
}
bootstrapApplication(App).catch(console.error);
