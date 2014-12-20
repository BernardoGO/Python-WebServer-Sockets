def include(filename):
    file_handler = open(filename,'rb')
    text = file_handler.read()
    codeOut = StringIO.StringIO()
    sys.stdout = codeOut
    exec(text)
    sys.stdout = sys.__stdout__
    response2 = codeOut.getvalue()
    return response2
