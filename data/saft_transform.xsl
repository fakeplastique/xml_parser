<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:saft="http://www.saf-t.ua/schema/1.0">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>

    <xsl:template match="/">
        <html>
            <head>
                <title>SAF-T UA Audit Report</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f5f5f5;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #34495e;
                        background-color: #ecf0f1;
                        padding: 10px;
                        margin-top: 20px;
                        border-left: 4px solid #3498db;
                    }
                    h3 {
                        color: #7f8c8d;
                        margin-top: 15px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 15px 0;
                        background-color: white;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    th {
                        background-color: #3498db;
                        color: white;
                        padding: 12px;
                        text-align: left;
                        font-weight: bold;
                    }
                    td {
                        padding: 10px;
                        border-bottom: 1px solid #ddd;
                    }
                    tr:hover {
                        background-color: #f8f9fa;
                    }
                    .header-info {
                        background-color: white;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .info-row {
                        margin: 8px 0;
                    }
                    .label {
                        font-weight: bold;
                        color: #2c3e50;
                        display: inline-block;
                        width: 250px;
                    }
                    .value {
                        color: #34495e;
                    }
                    .total {
                        background-color: #e8f5e9;
                        font-weight: bold;
                    }
                    .invoice-section {
                        background-color: white;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        border-left: 4px solid #2ecc71;
                    }
                </style>
            </head>
            <body>
                <h1>SAF-T UA Audit File Report</h1>

                <!-- Header Information -->
                <xsl:apply-templates select="//saft:Header | //Header"/>

                <!-- Master Files -->
                <h2>Master Files</h2>
                <xsl:apply-templates select="//saft:MasterFiles | //MasterFiles"/>

                <!-- Source Documents -->
                <h2>Source Documents</h2>
                <xsl:apply-templates select="//saft:SourceDocuments | //SourceDocuments"/>
            </body>
        </html>
    </xsl:template>

    <!-- Header Template -->
    <xsl:template match="Header | saft:Header">
        <div class="header-info">
            <h2>Company Information</h2>
            <div class="info-row">
                <span class="label">Company Name:</span>
                <span class="value"><xsl:value-of select="CompanyName | saft:CompanyName"/></span>
            </div>
            <div class="info-row">
                <span class="label">Company ID:</span>
                <span class="value"><xsl:value-of select="CompanyID | saft:CompanyID"/></span>
            </div>
            <div class="info-row">
                <span class="label">Tax Registration Number:</span>
                <span class="value"><xsl:value-of select="TaxRegistrationNumber | saft:TaxRegistrationNumber"/></span>
            </div>
            <div class="info-row">
                <span class="label">Audit File Version:</span>
                <span class="value"><xsl:value-of select="AuditFileVersion | saft:AuditFileVersion"/></span>
            </div>
            <div class="info-row">
                <span class="label">Date Created:</span>
                <span class="value"><xsl:value-of select="AuditFileDateCreated | saft:AuditFileDateCreated"/></span>
            </div>
            <div class="info-row">
                <span class="label">Tax Accounting Basis:</span>
                <span class="value"><xsl:value-of select="TaxAccountingBasis | saft:TaxAccountingBasis"/></span>
            </div>
        </div>
    </xsl:template>

    <!-- Master Files Template -->
    <xsl:template match="MasterFiles | saft:MasterFiles">
        <!-- Accounts -->
        <h3>General Ledger Accounts</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Account ID</th>
                <th>Description</th>
                <th>Type</th>
                <th>Debit Balance</th>
                <th>Credit Balance</th>
            </tr>
            <xsl:for-each select="GeneralLedgerAccounts/Account | saft:GeneralLedgerAccounts/saft:Account">
                <tr>
                    <td><xsl:value-of select="@id"/></td>
                    <td><xsl:value-of select="AccountID | saft:AccountID"/></td>
                    <td><xsl:value-of select="AccountDescription | saft:AccountDescription"/></td>
                    <td><xsl:value-of select="@type"/></td>
                    <td><xsl:value-of select="OpeningDebitBalance | saft:OpeningDebitBalance"/></td>
                    <td><xsl:value-of select="OpeningCreditBalance | saft:OpeningCreditBalance"/></td>
                </tr>
            </xsl:for-each>
        </table>

        <!-- Customers -->
        <h3>Customers</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Customer ID</th>
                <th>Company Name</th>
                <th>Tax ID</th>
                <th>Type</th>
                <th>Contact</th>
                <th>City</th>
            </tr>
            <xsl:for-each select="Customers/Customer | saft:Customers/saft:Customer">
                <tr>
                    <td><xsl:value-of select="@id"/></td>
                    <td><xsl:value-of select="CustomerID | saft:CustomerID"/></td>
                    <td><xsl:value-of select="CompanyName | saft:CompanyName"/></td>
                    <td><xsl:value-of select="CustomerTaxID | saft:CustomerTaxID"/></td>
                    <td><xsl:value-of select="@type"/></td>
                    <td><xsl:value-of select="Contact/ContactPerson | saft:Contact/saft:ContactPerson"/></td>
                    <td><xsl:value-of select="BillingAddress/City | saft:BillingAddress/saft:City"/></td>
                </tr>
            </xsl:for-each>
        </table>

        <!-- Suppliers -->
        <h3>Suppliers</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Supplier ID</th>
                <th>Company Name</th>
                <th>Tax ID</th>
                <th>Contact Person</th>
                <th>Telephone</th>
            </tr>
            <xsl:for-each select="Suppliers/Supplier | saft:Suppliers/saft:Supplier">
                <tr>
                    <td><xsl:value-of select="@id"/></td>
                    <td><xsl:value-of select="SupplierID | saft:SupplierID"/></td>
                    <td><xsl:value-of select="CompanyName | saft:CompanyName"/></td>
                    <td><xsl:value-of select="SupplierTaxID | saft:SupplierTaxID"/></td>
                    <td><xsl:value-of select="Contact/ContactPerson | saft:Contact/saft:ContactPerson"/></td>
                    <td><xsl:value-of select="Contact/Telephone | saft:Contact/saft:Telephone"/></td>
                </tr>
            </xsl:for-each>
        </table>

        <!-- Products -->
        <h3>Products</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Product Code</th>
                <th>Description</th>
                <th>Category</th>
                <th>Unit Price</th>
                <th>Unit of Measure</th>
            </tr>
            <xsl:for-each select="Products/Product | saft:Products/saft:Product">
                <tr>
                    <td><xsl:value-of select="@id"/></td>
                    <td><xsl:value-of select="ProductCode | saft:ProductCode"/></td>
                    <td><xsl:value-of select="ProductDescription | saft:ProductDescription"/></td>
                    <td><xsl:value-of select="@category"/></td>
                    <td><xsl:value-of select="UnitPrice | saft:UnitPrice"/></td>
                    <td><xsl:value-of select="UnitOfMeasure | saft:UnitOfMeasure"/></td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

    <!-- Source Documents Template -->
    <xsl:template match="SourceDocuments | saft:SourceDocuments">
        <h3>Sales Invoices</h3>
        <xsl:for-each select="SalesInvoices/Invoice | saft:SalesInvoices/saft:Invoice">
            <div class="invoice-section">
                <h4>Invoice: <xsl:value-of select="InvoiceNo | saft:InvoiceNo"/></h4>
                <div class="info-row">
                    <span class="label">Invoice ID:</span>
                    <span class="value"><xsl:value-of select="@id"/></span>
                </div>
                <div class="info-row">
                    <span class="label">Date:</span>
                    <span class="value"><xsl:value-of select="InvoiceDate | saft:InvoiceDate"/></span>
                </div>
                <div class="info-row">
                    <span class="label">Customer ID:</span>
                    <span class="value"><xsl:value-of select="CustomerID | saft:CustomerID"/></span>
                </div>
                <div class="info-row">
                    <span class="label">Type:</span>
                    <span class="value"><xsl:value-of select="@type"/></span>
                </div>
                <div class="info-row">
                    <span class="label">Paid:</span>
                    <span class="value"><xsl:value-of select="@paid"/></span>
                </div>

                <table>
                    <tr>
                        <th>Line</th>
                        <th>Product Code</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Line Amount</th>
                        <th>Tax Rate</th>
                        <th>Tax Amount</th>
                        <th>Total Amount</th>
                    </tr>
                    <xsl:for-each select="InvoiceLines/Line | saft:InvoiceLines/saft:Line">
                        <tr>
                            <td><xsl:value-of select="@lineNumber"/></td>
                            <td><xsl:value-of select="ProductCode | saft:ProductCode"/></td>
                            <td><xsl:value-of select="Quantity | saft:Quantity"/></td>
                            <td><xsl:value-of select="UnitPrice | saft:UnitPrice"/></td>
                            <td><xsl:value-of select="LineAmount | saft:LineAmount"/></td>
                            <td><xsl:value-of select="TaxRate | saft:TaxRate"/>%</td>
                            <td><xsl:value-of select="TaxAmount | saft:TaxAmount"/></td>
                            <td><xsl:value-of select="TotalAmount | saft:TotalAmount"/></td>
                        </tr>
                    </xsl:for-each>
                    <tr class="total">
                        <td colspan="7">Net Total:</td>
                        <td><xsl:value-of select="DocumentTotals/NetTotal | saft:DocumentTotals/saft:NetTotal"/></td>
                    </tr>
                    <tr class="total">
                        <td colspan="7">Tax Payable:</td>
                        <td><xsl:value-of select="DocumentTotals/TaxPayable | saft:DocumentTotals/saft:TaxPayable"/></td>
                    </tr>
                    <tr class="total">
                        <td colspan="7">Gross Total:</td>
                        <td><xsl:value-of select="DocumentTotals/GrossTotal | saft:DocumentTotals/saft:GrossTotal"/></td>
                    </tr>
                </table>
            </div>
        </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>
