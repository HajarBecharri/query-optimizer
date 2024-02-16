import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
interface QueryResponse {
  results: any;
  executionPlan: any;
  queryOptimized:any;
  excutionTime:any;

}

@Injectable({
  providedIn: 'root'
})
export class QueryService {

  url:string = "http://127.0.0.1:5000";

  httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' })
  };

  constructor(private http:HttpClient) { }
  executeQuery(query:string): Observable<QueryResponse>{

    return this.http.post<QueryResponse>(this.url+"/execute_query" , {query}, this.httpOptions );

  }
  
}
