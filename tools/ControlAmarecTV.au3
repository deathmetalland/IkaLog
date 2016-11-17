;
;  IkaLog
;  ======
;  Copyright (C) 2015 Takeshi HASEGAWA
;
;  Licensed under the Apache License, Version 2.0 (the 'License');
;  you may not use this file except in compliance with the License.
;  You may obtain a copy of the License at
;
;      http://www.apache.org/licenses/LICENSE-2.0
;
;  Unless required by applicable law or agreed to in writing, software
;  distributed under the License is distributed on an 'AS IS' BASIS,
;  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;  See the License for the specific language governing permissions and
;  limitations under the License.

;
;  Start and stop recording using Open Broadcaster Software(OBS).
;
;  To Start Recording:
;    ControlAmarecTV.au3 start
;
;  To Stop Recording:
;    ControlAmarecTV.au3 stop
;
;  To Reanem the recording:
;    If you want to rename the recording to a specific filename,
;    Specifcy the filename as environment variables
;    IKALOG_MP4_DESTDIR and IKALOG_MP4_DESTNAME.
;
;  Though this script will sleep seconds so that work on
;  a specific environment. The behavior is subject to change.
;

#include <FileConstants.au3>
#include <StringConstants.au3>


;���ƍD�݂ɍ��킹�Ēl��ݒ肵�Ă��������B
;Send�L�[�̒l�̏������ɂ���  https://www.autoitscript.com/autoit3/docs/appendix/SendKeys.htm
Const $SendKeyValue = "^z"      ;AmaRecTV�̘^��J�n�ɐݒ肳��Ă���L�[�̒l
Const $STARTsleepSec = 0        ;�^��J�n�̑ҋ@���ԁi�b�Ŏw��j
Const $STOPsleepSec = 10        ;�^��I���̑ҋ@���ԁi�b�Ŏw��j
Const $RENAMEsleepSec = 3       ;�^��I���ナ�l�[�������܂ł̑ҋ@���ԁi�b�Ŏw��j


Func RenameFile($source)
    Local $dest = EnvGet('IKALOG_MP4_DESTNAME')
    $dest = StringReplace($dest, "/", "\")
    If $dest = '' Then
        Return False
    EndIf
    
    ; IkaLog assumes mp4 as video file extension, but AmarecTV uses avi.
    If StringRight($dest, 4) = ".mp4" Then
        $dest = StringReplace($dest, ".mp4", ".avi", -1)
    EndIf
    
    FileMove($source, $dest, $FC_OVERWRITE)
EndFunc

Func FindRecentRecording()
    Local $directory = EnvGet('IKALOG_MP4_DESTDIR')

    ; Replace all slashes to backslashes.
    ; $directory also needs a backslash at its end.
    $directory = StringReplace($directory, "/", "\")
    If StringRight($directory, 1) <> "\" Then
        $directory = $directory & "\"
    EndIf
    
    Local $hSearch = FileFindFirstFile($directory & "*.avi*")
    
    If $hSearch = -1 Then
        MsgBox(0, "Error", "Could not find any candinates in " & $directory & " (path 1)", 10)
        Return False
    EndIf
    
    Local $latest_file = ''
    Local $latest_timestamp = ''
    
    While True
        Local $file = FileFindNextFile($hSearch)
        If @error Then ExitLoop
    
        Local $timestamp = FileGetTime($directory & $file, $FT_MODIFIED, $FT_STRING)
        If StringCompare($timestamp, $latest_timestamp) > 0 Then
            $latest_file = $directory & $file
            $latest_timestamp = $timestamp
        EndIf
    WEnd
    
    FileClose($hSearch)
    
    If $latest_file = '' Then
        MsgBox(0, "Error", "Could not find any candinates in " & $directory & " (path 2)", 10)
        Return False
    EndIf
    
    Return $latest_file
EndFunc

Func ControlAmarecTV($stop)
    Local $hWnd = 0
    If WinExists('[CLASS:AmaRecTV; INSTANCE:2]') Then
        $hWnd = WinWait('[CLASS:AmaRecTV; INSTANCE:2]', '', 1)
    Else
        $hWnd = WinWait('[CLASS:AmaRecTV4; INSTANCE:2]', '', 1)
    EndIf

    If $hWnd = 0 Then
        MsgBox(0, "Error", "Could not find AmarecTV")
        Return False
    EndIf

    Local $text = ControlGetText($hWnd, "", "[CLASS:msctls_statusbar32]")
    Local $inRecording = StringInStr($text, '�^�撆...') > 0

    ;���X�g����擾�����n���h���Ɣ�r����,�Ⴄ�Ƃ��̓t���[���Ȃ��Ƃ݂Ȃ�����ւ���
    Local $ListhWnd = GetAmaRecHandleFromList()
    If ($ListhWnd <> 0) And ($ListhWnd <> $hWnd) Then
        $hWnd = $ListhWnd
    EndIf

    Local $click = False
    If $inRecording and $stop Then
        ;Stop Recording.
        $click = True
    ElseIf (Not $inRecording) and (Not $stop) Then
        ; Start Recording.
        $click = True
    EndIf

    If $click Then
        If $stop Then
            ; �^��I���ҋ@
            Sleep(1000 * $STOPsleepSec)
        Else
            ; �^��J�n�ҋ@
            Sleep(1000 * $STARTsleepSec)
        EndIf

        WinActivate($hWnd)
        WinWaitActive($hWnd, "", 1)

        ; SendKey
        Send($SendkeyValue)

        If $stop Then
            If EnvGet('IKALOG_MP4_DESTDIR') <> "" Then
                Sleep(1000 * $RENAMEsleepSec)
                Local $file  = FindRecentRecording()
                RenameFile($file)
            EndIf
        EndIf
    EndIf
EndFunc

;�E�C���h�E���������A�^�C�g����AmaRecTV, �N���X����Display���܂܂�Ă���A�����AmaRecTV�ƔF�����ăn���h����Ԃ�
Func IsVisible($handle)
    If BitAnd( WinGetState($handle), 2 ) Then
        Return 1
    Else
        Return 0
    EndIf
EndFunc

; $var[$i][0]:�^�C�g��, $var[$i][1]:�n���h��
Func GetAmaRecHandleFromList()
    Local $var = WinList()
    Local $retValue = 0
    For $i = 1 to $var[0][0]
        ; ���Ŗ��O�̂���E�B���h�E�̂�
        If $var[$i][0] <> "" AND IsVisible($var[$i][1]) Then
            If StringInStr($var[$i][0], "AmaRecTV") Or StringInStr($var[$i][0], "AmaRecTV4") Then
                If (StringInStr(WinGetClassList($var[$i][0]), "Display")) Then
                    $retValue = $var[$i][1]
                    Return $retValue
                EndIf
            EndIf
        EndIf
    Next
    Return $retValue
EndFunc

if ($CmdLine[0] = 0) Then
    Local $msg = StringFormat("%s%s", "--- �N���I�v�V����---", @LF)
    $msg = StringFormat("%s%s%s%s%s",$msg, "�^��J�n:", @ScriptName, " start", @LF)
    $msg = StringFormat("%s%s%s%s", $msg, "�^��I��:", @ScriptName, " stop" & @LF & @LF)
    $msg = StringFormat("%s%s%s", $msg, "--- ���݂̐ݒ� --- ", @LF)
    $msg = StringFormat("%s%s%s%s", $msg, "�z�b�g�L�[�̒l: ", $SendKeyValue, @LF)
    $msg = StringFormat("%s�^��J�n�̑ҋ@���� %s�b%s", $msg, $STARTsleepSec, @LF)
    $msg = StringFormat("%s�^��I���̑ҋ@���� %s�b%s", $msg, $STOPsleepSec,  @LF)
    $msg = StringFormat("%s���l�[���̑ҋ@���� %s�b%s", $msg, $RENAMEsleepSec, @LF)
    MsgBox(64, "�N���I�v�V���� & ���݂̐ݒ�", $msg)
Else
    $stop = StringCompare($CmdLine[1], 'stop') == 0
    ControlAmarecTV($stop)
EndIf
