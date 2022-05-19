.text
.global  set_tod_from_secs
        
## ENTRY POINT FOR REQUIRED FUNCTION
set_tod_from_secs:
	movl	%edi, %eax 		 		 #moves input to 32 bit eax register
	cmpl	$0, %eax 				 #compare 0 to number of seconds
	jl	.FAIL   				 #jumps to fail if %eax is less than 0
	cmpl	$86400, %eax 				 #compare max seconds in day to number of seconds
	jge	.FAIL     				 #jumps to fail if %eax greater than or equal to max seconds in day
	xor	%edx, %edx				 #zero out %edx
	movl	$3600, %ecx				 #putting what we are dividing by into %ecx register
	idiv	%ecx					 #result goes into %eax, remainder goes to %edx
	cmpl	$12, %eax				 #comparing 12 to number of hours to get ampm
	jl	.AM					 #jumps to set AM if less than 12
	cmpl	$12, %eax	
	jg	.PM					 #jumps to set PM if greater than 12
	movb	$2, 6(%rsi)				 #special case for 12
	jmp	.MINUTES
	
.PM:
	movb	$2, 6(%rsi)		#sets ampm to 2 for pm
	sub	$12, %eax		#removes 12 from values greater than 12
	jmp	.MINUTES
	
.AM:
	movb	$1, 6(%rsi)		#set ampm to 1 for am
	cmp	$0, %eax		#checks for midnight
	je	.MIDNIGHT		#goes to 12 if 0
	jmp	.MINUTES

.MIDNIGHT:
	add	$12, %eax		#adds 12
	jmp	.MINUTES
	
.MINUTES:
	movw	%ax, (%rsi)		#moves result in 2 bytes from %eax to hours field
	movl	%edx, %eax		#moves remainder to %eax to be divided again
	xor	%edx, %edx		#zero out edx
	movl	$60, %ecx		#moves what we are dividing by to %ecx
	idiv	%ecx			#remainder in %edx, result in %eax
	movw	%ax, 2(%rsi)		#moves result to minutes field
	movw	%dx, 4(%rsi)		#remainder is number of seconds, moves to seconds field
	xor	%eax, %eax		#return value zeroed
	ret
	
.FAIL:
	movl	$1, %eax		#return value of 1 for bad input
	ret
      

### Data area associated with the next function
.data

masks:                      	 # declare multiple ints in a row 
        .int 0b0111111      	 #masks in order from 0-9 in the order they are in the array       
        .int 0b0110000                 
        .int 0b1101101
        .int 0b1111001
        .int 0b1110010
        .int 0b1011011
        .int 0b1011111
        .int 0b0110001
        .int 0b1111111
        .int 0b1111011
        .int 0b0000000     	#blank for tens place of hours hand


.text
.global  set_display_from_tod

## ENTRY POINT FOR REQUIRED FUNCTION
set_display_from_tod:
        #tod_t in rdi
        #pointer to display int in rsi
        #catches bad input values
        movq	%rdi, %r8
        cmpw	$0, %r8w		#comparing hours portion to 0, di is first 16 bits
        jl	.BADVAL		#if less than zero goes to failure
        cmpw	$12, %r8w		#compare hours to 12
        jg	.BADVAL		#fail if hours >12
        shrq	$16, %r8
        cmpw	$0, %r8w		#16 into 32 bit edi register compares next 16 bits
        jl	.BADVAL
        cmpw	$59, %r8w		#compares to max of 59
        jg	.BADVAL
        shrq	$16, %r8
        cmpw	$0, %r8w		#32 bits into 64 bit register accesses seconds
        jl	.BADVAL
        cmpb	$59, %r8b		#compares seconds value to max of 59
        jg	.BADVAL
        jmp	.MINUTES_ONES
        
.MINUTES_ONES:   
        leaq	masks(%rip), %r8	#r8 points to mask array
        pushq	%r12
        movq	%rdi, %r12
        shrq	$16, %r12
        movq	$0, %r11		#zero out display integer values in temp holder register
        xor	%edx, %edx		#zero out edx for division
        xor	%eax, %eax
        movl	$10, %ecx		#what we are dividing by
        movw	%r12w, %ax		#moving minutes into eax register
        idiv	%ecx			#remainder in edx, result in eax (minutes ones is remainder so it is in edx)
        movl	%edx, %r9d		#gets value of minutes ones
        movl	(%r8,%r9,4),%r10d	#r10d=array[minutes ones]
        orl	%r10d,%r11d		#sets minutes tens spot with mask
        popq	%r12
        jmp	.MINUTES_TENS
        
.MINUTES_TENS:
	xor	%edx, %edx		#clears edx for division again
	idiv	%ecx			#divides by 10 again, remainder stored in edx is number we want
	movl	%edx, %r9d		#moving minutes tens into r9 to access mask array
	movl	(%r8,%r9,4),%r10d	#sets r10d to bitmask at array [minutes tens]
	shll	$7, %r10d		#shifts mask to start at 8th bit
	orl	%r10d,%r11d		#sets next  bits of rsi display to be mask of tens digit
	jmp	.HOURS_ONES

.HOURS_ONES:
	xor	%edx, %edx		#clear edx
	movw	%di, %ax		#first 16 bits is hours, moved into eax register
	idiv	%ecx			#remainder in edx is value we want
	movl	%edx, %r9d		#moves result into index value
	movl	(%r8,%r9,4),%r10d	#r10d is mask
	shll	$14, %r10d		#shift 14 to left
	orl	%r10d, %r11d		#masks next bits
	jmp	.HOURS_TENS
	
.HOURS_TENS:
	xor	%edx, %edx
	idiv	%ecx			#dividing by 10 to get remainder equal to the hours tens spot, held in edx
	cmpl	$0, %edx		#checking if 0 for blank mask
	je	.BLANK			#if it needs a blank mask jumps to blank mask function
	movq	$1, %r9		#if it is not blank it must be 1
	movl	(%r8,%r9,4),%r10d	#r10d becomes mask for number 1
	shll	$21, %r10d		#shifting bits left by 21
	orl	%r10d, %r11d		#sets next 2 bytes to be bitmask
	jmp	.CHECKAMPM		
	
	
.CHECKAMPM:
	shrq	$48, %rdi
	cmpb	$1, %dil		#checking for am or pm
	je	.SETAM			#conditional if ampm equals 1
	cmpb	$2, %dil	#checks for 2 to set pm
	je	.SETPM
	jmp	.BADVAL		#neither 1 or 2 so something is wrong
	
.SETAM:
	movl	$1, %edx		#for bitshift
	shll	$28, %edx		#edx now had a 1 at bit 28, 0 everywhere else
	orl	%edx, %r11d		#28 set for am
	movl	%r11d, (%rsi)
	movl	$0, %eax		#return value of 0
	ret
.SETPM:
	movl	$1, %edx		#for bitshift
	shll	$29, %edx		#edx now had a 1 at bit 29, 0 everywhere else
	orl	%edx, %r11d		#29 set for pm
	movl	%r11d, (%rsi)
	movl	$0, %eax		#return value 0
	ret
	
.BLANK:
	movq	$10, %r9		#blank mask is at pos 10 in mask array
	movl	(%r8,%r9,4),%r10d	#setting r10d to blank mask
	shll	$21, %r10d		#shifting bits left by 21
	orl	%r10d, %r11d	#blank bit mask for next 8 bits
	jmp	.CHECKAMPM
        
.BADVAL:
	movl	$1, %eax		#return value of one
	ret

.text
.global clock_update
        
## ENTRY POINT FOR REQUIRED FUNCTION
clock_update:
	subq	$8, %rsp				#space on stack
	movq	$0, (%rsp)				#0 now at adress rsp points to (tod t struct)
	leaq	(%rsp), %rsi				#rsi now holds pointer (arg 2)
	movl	TIME_OF_DAY_SEC(%rip),%edi		#arg 1 is global seconds
	call	set_tod_from_secs			#calls first function
	cmpl	$0, %eax				#checks return value
	jne	.ERROR					#jumps if return value not 0
	movq	(%rsp), %rdi				#value of what is pointed to by rsi is now rdi (arg1)
	pushq	%rdx					#setting up stack memory for struct
	pushq	%r12					#gets used in display func
	leaq	CLOCK_DISPLAY_PORT(%rip), %rsi		#pointer to global display int in arg 2
	call	set_display_from_tod			#struct in rdi, pointer to display in rsi, Problem 30 fails in this function???
	popq	%r12					#popping r12 now that function its used it has been called
	cmpl	$0, %eax				#checking return value of function
	jne	.ERROR	
	addq	$8, %rsp				#fixing stack
	popq	%rdx					#popping register we pushed
	ret
.ERROR:
	addq	$8, %rsp				#fixing stack
	popq	%rdx					#cleans up stack
	movl	$1, %eax
	ret
	
