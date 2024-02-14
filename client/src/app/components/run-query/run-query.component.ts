import { Component } from '@angular/core';
import { QueryService } from 'src/app/services/query.service';
interface QueryResponse {
  results: any;
  executionPlan: any;
}

@Component({
  selector: 'app-run-query',
  templateUrl: './run-query.component.html',
  styleUrls: ['./run-query.component.css']
})



export class RunQueryComponent {
  
    query!: string;
    response!: QueryResponse;
  
    constructor(private queryService: QueryService) { }
  
    executeQuery() {
      this.queryService.executeQuery(this.query).subscribe(
        (response: QueryResponse) => {
          this.response = response;
          console.log(this.response.executionPlan);
        },
        (error) => {
          console.error('Error executing query:', error);
        }
      );
    }

}
