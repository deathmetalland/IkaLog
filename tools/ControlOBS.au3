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
;    ControlOBS.au3 start
;
;  To Stop Recording:
;    ControlOBS.au3 stop
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
Const $STARTsleepSec = 0    ;�^��J�n�̑ҋ@���ԁi�b�Ŏw��j
Const $STOPsleepSec = 10    ;�^��I���̑ҋ@���ԁi�b�Ŏw��j
Const $RENAMEsleepSec = 3   ;�^��I���ナ�l�[�������܂ł̑ҋ@���ԁi�b�Ŏw��j


Func RenameFile($source)
	Local $dest = EnvGet('IKALOG_MP4_DESTNAME')
	$dest = StringReplace($dest, "/", "\")
	If $dest = '' Then
		Return False
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

	Local $hSearch = FileFindFirstFile($directory & '*.mp4')

	If $hSearch = -1 Then
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
		Return False
	EndIf

	Return $latest_file
EndFunc

Func ControlOBS($stop)
    Local $hWnd = WinWait('[CLASS:OBSWindowClass]', '', 1)

	If $hWnd == 0 Then
		Return False
	EndIf

	; Get current state.
	Local $l = ControlGetText ($hWnd, '', 'Button5')

	Local $inRecording_ja = (StringCompare($l, '�^���~') == 0)
	Local $inRecording_en = (StringCompare($l, 'Stop Recording') == 0)
	Local $inRecording = $inRecording_ja or $inRecording_en

	Local $click = False
	If $inRecording and $stop Then
		# Stop Recording.
		$click = True
	ElseIf (Not $inRecording) and (Not $stop) Then
		# Start Recording.
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

		ControlClick($hWnd, '', 'Button5')

		If $stop Then
			Sleep(1000 * $RENAMEsleepSec)
			Local $file  = FindRecentRecording()
			RenameFile($file)
		EndIf
	EndIf
EndFunc


Func DetectOBSMultiPlatform()
    Local $hWnd = WinWait('[CLASS:Qt5QWindowIcon;REGEXPTITLE:OBS\s]', '', 1)

	If $hWnd == 0 Then
		Return False
	EndIf

    Return True
EndFunc



if ($CmdLine[0] = 0) Then	;exe�ɃR���o�[�g������ �m�F�ɕ֗����Ȃƍl���ǉ�
   Local $msg = StringFormat("%s%s",     "--- �N���I�v�V����---", @LF)
   $msg = StringFormat("%s%s%s%s%s",$msg, "�^��J�n:", @ScriptName, " start", @LF)
   $msg = StringFormat("%s%s%s%s", $msg, "�^��I��:", @ScriptName, " stop" & @LF & @LF)
   $msg = StringFormat("%s%s%s",    $msg, "--- ���݂̐ݒ� --- ", @LF)
   $msg = StringFormat("%s�^��J�n�̑ҋ@���� %s�b%s", $msg, $STARTsleepSec, @LF)
   $msg = StringFormat("%s�^��I���̑ҋ@���� %s�b%s", $msg, $STOPsleepSec,  @LF)
   $msg = StringFormat("%s���l�[���̑ҋ@���� %s�b%s", $msg, $RENAMEsleepSec, @LF)
   MsgBox(64, "�N���I�v�V���� & ���݂̐ݒ�", $msg)

   if (DetectOBSMultiPlatform()) Then
       MsgBox(64, "Detected OBS Multiplatform", "This script supports OBS Classic only")
   EndIf

Else
   $stop = StringCompare($CmdLine[1], 'stop') == 0
   ControlOBS($stop)
EndIf
