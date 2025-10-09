import gurobipy as gp
from gurobipy import GRB

class InputData:
    def __init__(self, VARIABLES, objective_coeff, constraints_coeff, constraints_rhs, constraints_sense):
        self.VARIABLES = VARIABLES
        self.objective_coeff = objective_coeff
        self.constraints_coeff = constraints_coeff
        self.constraints_rhs = constraints_rhs
        self.constraints_sense = constraints_sense

class LP_OptimizationProblem:

    def __init__(self, input_data: InputData): 
        self.data = input_data 
        self.results = type("Expando", (), {})()  # simple dummy expando
        self._build_model() 
    
    def _build_variables(self):
        self.variables = {v: self.model.addVar(lb=0, name=v) for v in self.data.VARIABLES}
    
    def _build_constraints(self):
        self.constraints = []
        for i in range(len(self.data.constraints_rhs)):
            lhs = gp.quicksum(self.data.constraints_coeff[v][i] * self.variables[v] for v in self.data.VARIABLES)
            constr = self.model.addLConstr(lhs,
                                           self.data.constraints_sense[i],
                                           self.data.constraints_rhs[i],
                                           name=f"constr[{i}]")
            self.constraints.append(constr)

    def _build_objective_function(self):
        objective = gp.quicksum(self.data.objective_coeff[v] * self.variables[v] for v in self.data.VARIABLES)
        self.model.setObjective(objective, GRB.MINIMIZE)

    def _build_model(self):
        self.model = gp.Model(name='Consumer Flexibility')
        self._build_variables()
        self._build_objective_function()
        self._build_constraints()
        self.model.update()
    
    def _save_results(self):
        self.results.objective_value = self.model.ObjVal
        self.results.variables = {v: self.variables[v].X for v in self.data.VARIABLES}
        self.results.duals = {f"constr[{i}]": self.constraints[i].Pi for i in range(len(self.constraints))}

    def run(self):
        self.model.optimize()
        if self.model.status == GRB.OPTIMAL:
            self._save_results()
        else:
            print(f"optimization of {self.model.ModelName} was not successful")
    
    def display_results(self):
        print("\n-------------------   RESULTS  -------------------")
        print("Optimal objective value:", self.results.objective_value)
        print("Optimal variable values:", self.results.variables)
        print("Optimal dual values:", self.results.duals)