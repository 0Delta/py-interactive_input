from input import Object


def testenc(e: str) -> str:
    return "base64ed: " + e


def ValidTest(e: str) -> bool:
    return e.find('ng') < 0


if __name__ == '__main__':
    test = Object()
    test.setVerbose(verbose="test is very loooooooooooooooooooooooooooooooooooo\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("key2", message="hoge-fuge", default=None)
    test.AddQ("key", message="loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("keyA", message="looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat",
              message_wrap=True)
    test.AddQ("keyB", message="looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo\n\n\noooooooooooongcat",
              message_wrap=True)
    test.AddQ("keyC", message="looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("keyD", message="looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("keyE", message="looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongcat")
    test.AddQ("key3", hook=testenc, validator=ValidTest)
    ret = test.Ask()
    test.freeze("key2")
    test.AddQ("key4", hook=testenc, default="aaa")
    test.AddQ("key5", hook=testenc, default="5")
    ret = test.Ask()
    print(test)
    print(ret)
