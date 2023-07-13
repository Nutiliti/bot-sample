from parsers.utils import Parser,validate, create_new_results, res

def parse(pdf):
    results = create_new_results()

    results["pdfBalance"] = Parser(pdf).page(1).directly_after("TotalElectricServiceAmount").is_dollars().exec()
    results["dueDate"] = Parser(pdf).page(1).directly_after("AmountDueBy:").is_date('%b%d,%Y').exec()
    results["billAvailableDate"] = Parser(pdf).page(1).directly_after("BillingDate:").is_date('%b%d,%Y').exec()
    results["autopayDate"] = results["dueDate"]
    results["billDateRange"] = Parser(pdf).page(1).directly_after("kWh").args(x_tolerance=0.3).is_date_range("%b %d, %Y","to").exec()
    return results