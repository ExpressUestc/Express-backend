from Express.utils import decrypt


def decryptPostInfo(request,*fields):
    L = []
    for field in fields:
        L.append(decrypt.decryptMessage(request.POST[field]))
    return L